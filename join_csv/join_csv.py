import csv
import argparse

def flatten_csv(file_path, column_mapping, headers):
    corrected_data = []
    server_dict = {}
    current_server_code = None

    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            if len(row) != len(headers):
                try:
                    row += next(csv_reader, [])
                except StopIteration:
                    continue  

            category, description, details, start_date, end_date, quantity, price, total_cost, ipv4 = row

            if "Cloud Project" in category:
                continue

            server_code = extract_code(details)

            if ipv4 or current_server_code is None:  # Nueva fila de servidor o la primera fila
                current_server_code = server_code
                custom_server_name = extract_server_name(details)
                ipv4 = extract_ipv4_from_row(details, description)
                extras_price = 0

                current_server = {
                    column_mapping['start_date']: start_date,
                    column_mapping['end_date']: end_date,
                    column_mapping['quantity']: float(quantity),
                    column_mapping['price']: float(price),
                    'server_code': server_code,
                    'custom_server_name': custom_server_name,
                    'ipv4': ipv4,
                    'extras_price': extras_price,
                    'extra_quantity': 0 
                }

                server_dict[server_code] = current_server
            elif current_server_code and current_server_code in server_dict:  
                extra_price = float(price)
                extra_quantity = float(quantity)
                server_dict[current_server_code]['extras_price'] += extra_price * extra_quantity
                server_dict[current_server_code]['extra_quantity'] += extra_quantity
                extra_ipv4 = extract_ipv4_from_row(details, description)
                if server_dict[current_server_code]['ipv4'] is None and extra_ipv4:
                    server_dict[current_server_code]['ipv4'] = extra_ipv4

    for server in server_dict.values():
        server[column_mapping['price']] = (server[column_mapping['quantity']] * server[column_mapping['price']]) + server['extras_price']

    corrected_data = list(server_dict.values())
    return corrected_data

def extract_code(details):
    if "#" in details:
        start = details.index("#") + 1
        end = details.find(",", start)
        if end == -1:  
            end = len(details)
        return details[start:end].strip()
    return None

def extract_server_name(details):
    if "\"" in details:
        start = details.index("\"") + 1
        end = details.index("\"", start)
        return details[start:end].strip()
    return None

def extract_ipv4(text):
    ipv4_index = text.find("x Primary IPv4")
    if ipv4_index != -1:
        start = text.find("\n", ipv4_index) + 1
        ipv4_text = text[start:].strip().split()[0]
        ipv4_text = ipv4_text.split(',')[0].strip()
        octets = ipv4_text.split('.')
        if len(octets) == 4 and all(octet.isdigit() and 0 <= int(octet) <= 255 for octet in octets):
            return ipv4_text
    return None

def extract_ipv4_from_row(details, description):
    ipv4_details = extract_ipv4(details)
    ipv4_description = extract_ipv4(description)
    return ipv4_details if ipv4_details else ipv4_description

def read_csv(file_path):
    data = []
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

def merge_dicts_with_priority(primary, secondary):
    result = primary.copy()
    for key, value in secondary.items():
        if key not in result or not result[key]:  
            result[key] = value
    return result

def merge_data(corrected_data, others, column_mapping):
    combined_data = {}
    combined_fields = set()

    for row in corrected_data:
        key = row.get('ipv4', None)
        if key:
            combined_data[key] = row
            combined_fields.update(row.keys())

    for file_path in others:
        rows = read_csv(file_path)
        for row in rows:
            key = row.get('ipv4_address', None)  
            if not key:
                key = row.get('ipv4', None)  
            if key:
                if key in combined_data:
                    combined_data[key] = merge_dicts_with_priority(combined_data[key], row)
                else:
                    combined_data[key] = row
                combined_fields.update(row.keys())

    final_fields = list(combined_fields)
    final_data = list(combined_data.values())
    return final_data, final_fields

def save_combined_csv(file_path, data, fields):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def save_headers(file_path, headers):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

def main():
    parser = argparse.ArgumentParser(description="Corrige un archivo CSV de factura y opcionalmente combina otros archivos CSV.")
    parser.add_argument('--invoice', required=True, help='Ruta del archivo CSV de la factura que se debe corregir')
    parser.add_argument('--output', required=True, help='Archivo CSV combinado resultante')
    parser.add_argument('--other', nargs='*', help='Rutas de otros archivos CSV opcionales')
    parser.add_argument('--headers', default="./hetzner_invoice.headers", help='Archivo CSV que contiene los encabezados')

    args = parser.parse_args()

    with open(args.headers, mode='r', newline='') as header_file:
        header_reader = csv.reader(header_file)
        headers = [header.strip() for header in next(header_reader)]  # Aplicamos .strip() a cada header

    column_mapping = {
        'start_date': headers[3],
        'end_date': headers[4],
        'quantity': headers[5],
        'price': headers[6]
    }

    output_file_path = args.output
    save_headers(output_file_path, headers)

    hetzner_data = flatten_csv(args.invoice, column_mapping, headers)

    other_files = args.other if args.other else []
    combined_data, combined_fields = merge_data(hetzner_data, other_files, column_mapping)

    save_combined_csv(output_file_path, combined_data, combined_fields)

if __name__ == "__main__":
    main()
