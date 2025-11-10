import sqlite3
import json
import csv
import xml.etree.ElementTree as ET
import os

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    print("Предупреждение: Библиотека PyYAML не установлена. YAML экспорт будет пропущен.")
    print("Установите: pip install PyYAML")
    YAML_AVAILABLE = False

class DatabaseExporter:
    def __init__(self, db_path=None):
        if db_path is None:
            possible_paths = [
                "hotel.db",
                "src/hotel.db",
                "../hotel.db"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    db_path = path
                    break
            else:
                db_path = "hotel.db"

        self.db_path = db_path
        print(f"Используется база данных: {db_path}")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_table_data_with_relations(self, table_name, relation_tables=None):
        cursor = self.conn.cursor()

        cursor.execute("PRAGMA table_info({})".format(table_name))
        table_columns = [row[1] for row in cursor.fetchall()]

        base_query = "SELECT * FROM {}".format(table_name)

        if relation_tables:
            joins = []
            select_columns = ["{}.{}".format(table_name, col) for col in table_columns]

            for rel_table, rel_condition in relation_tables.items():
                joins.append("LEFT JOIN {} ON {}".format(rel_table, rel_condition))
                cursor.execute("PRAGMA table_info({})".format(rel_table))
                rel_columns = [row[1] for row in cursor.fetchall()]
                select_columns.extend(["{}.{} as {}_{}".format(rel_table, col, rel_table, col) for col in rel_columns])

            query = "SELECT {} FROM {} {}".format(
                ", ".join(select_columns),
                table_name,
                " ".join(joins)
            )
        else:
            query = base_query

        print(f"Выполняется запрос: {query}")
        cursor.execute(query)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            row_dict = {}
            for key in row.keys():
                row_dict[key] = row[key]
            result.append(row_dict)

        return result

    def format_data_with_nesting(self, data, relation_tables=None):
        if not relation_tables:
            return data

        formatted_data = []
        for item in data:
            formatted_item = {}
            relations_data = {}

            for key, value in item.items():
                is_relation_field = False
                for rel_table in relation_tables.keys():
                    if key.startswith(rel_table + "_"):
                        is_relation_field = True
                        rel_field = key[len(rel_table) + 1:]
                        if rel_table not in relations_data:
                            relations_data[rel_table] = {}
                        relations_data[rel_table][rel_field] = value
                        break

                if not is_relation_field:
                    formatted_item[key] = value

            for rel_table, rel_data in relations_data.items():
                clean_rel_data = {k: v for k, v in rel_data.items() if v is not None}
                if clean_rel_data:
                    formatted_item[rel_table] = clean_rel_data

            formatted_data.append(formatted_item)

        return formatted_data

    def format_data_flat(self, data):
        flat_data = []
        for item in data:
            flat_item = {}
            for key, value in item.items():
                if isinstance(value, dict):
                    # Для вложенных словарей объединяем поля
                    for sub_key, sub_value in value.items():
                        flat_item[f"{key}_{sub_key}"] = sub_value
                else:
                    flat_item[key] = value
            flat_data.append(flat_item)
        return flat_data

    def export_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def export_to_csv(self, data, filename):
        if not data:
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                row_str = {k: str(v) if not isinstance(v, (str, int, float)) else v for k, v in row.items()}
                writer.writerow(row_str)

    def export_to_xml(self, data, filename, root_name="data", item_name="item"):
        root = ET.Element(root_name)

        for item in data:
            item_element = ET.SubElement(root, item_name)
            self._dict_to_xml(item, item_element)

        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)

    def _dict_to_xml(self, data, parent_element):
        for key, value in data.items():
            if isinstance(value, dict):
                child_element = ET.SubElement(parent_element, key)
                self._dict_to_xml(value, child_element)
            else:
                child_element = ET.SubElement(parent_element, key)
                child_element.text = str(value)

    def export_to_yaml(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def close(self):
        self.conn.close()

def main():
    os.makedirs('out', exist_ok=True)


    exporter = DatabaseExporter()


    try:
        table_name = "Booking"
        relation_tables = {
            "Room": "Booking.room_id = Room.room_id",
            "Client": "Booking.client_id = Client.client_id"
        }


        print("Получение данных из базы...")
        raw_data = exporter.get_table_data_with_relations(table_name, relation_tables)

        if not raw_data:
            print("Нет данных для экспорта")
            return


        nested_data = exporter.format_data_with_nesting(raw_data, relation_tables)
        flat_data = exporter.format_data_flat(nested_data)

        print("Экспорт в JSON...")
        exporter.export_to_json(nested_data, 'out/data.json')

        print("Экспорт в CSV...")
        exporter.export_to_csv(flat_data, 'out/data.csv')

        print("Экспорт в XML...")
        exporter.export_to_xml(nested_data, 'out/data.xml', 'bookings', 'booking')

        if YAML_AVAILABLE:
            print("Экспорт в YAML...")
            exporter.export_to_yaml(nested_data, 'out/data.yaml')
        else:
            print("Пропуск YAML экспорта (библиотека недоступна)")

        print("Экспорт завершен! Файлы созданы в папке 'out'")

        print(f"\nЭкспортировано записей: {len(raw_data)}")
        print("Созданные файлы:")
        files_to_check = ['data.json', 'data.csv', 'data.xml']
        if YAML_AVAILABLE:
            files_to_check.append('data.yaml')

        for file in files_to_check:
            filepath = os.path.join('out', file)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"  - {file} ({size} bytes)")

    except Exception as e:
        print(f"Ошибка при экспорте: {e}")
    finally:
        exporter.close()

if __name__ == "__main__":
    main()