#!/bin/bash

# Función para solicitar entrada de usuario con un mensaje y habilitar autocompletado de archivos
ask() {
  local prompt="$1"
  local value
  read -e -p "$prompt: " value
  echo "$value"
}

echo "- - - - - - - -"
# Solicita los parámetros uno por uno
invoice=$(ask "Introduce la ruta del archivo CSV de la factura que se debe corregir")
output=$(ask "Introduce el nombre o ruta del archivo CSV combinado resultante")

# Listar archivos CSV en el directorio actual, ignorando el archivo de factura
echo "Archivos CSV en el directorio actual (excluyendo el archivo de factura):"
csv_files=($(ls *.csv 2>/dev/null | grep -v "^$invoice$"))
for i in "${!csv_files[@]}"; do
  echo "$i: ${csv_files[$i]}"
done

# Pregunta si hay otros archivos CSV opcionales
read -p "¿Deseas combinar alguno de los archivos CSV listados? (s/n): " has_others
other_files=()
if [[ "$has_others" == "s" || "$has_others" == "S" ]]; then
  while true; do
    read -e -p "Introduce el nombre o el número del archivo CSV opcional (deja en blanco para terminar): " file_input
    if [[ -z "$file_input" ]]; then
      break
    elif [[ "$file_input" =~ ^[0-9]+$ ]] && [[ "$file_input" -ge 0 ]] && [[ "$file_input" -lt ${#csv_files[@]} ]]; then
      other_files+=("${csv_files[$file_input]}")
    elif [[ " ${csv_files[*]} " =~ " $file_input " ]]; then
      other_files+=("$file_input")
    else
      echo "Entrada inválida, por favor intenta de nuevo."
    fi
  done
fi

# Usa el archivo de encabezados por defecto o solicita otro
default_headers="./hetzner_invoice.headers"
headers=$(ask "Introduce la ruta del archivo separado por comas que contiene los encabezados de la factura (deja en blanco para usar el valor por defecto: $default_headers)")
headers=${headers:-$default_headers}

# Prepara el archivo de encabezados temporal
cp "$headers" "headers_tmp.csv"

# Construye los argumentos para el script Python
args=(--invoice "$invoice" --output "$output" --headers "headers_tmp.csv")
if [[ ${#other_files[@]} -gt 0 ]]; then
  args+=(--other "${other_files[@]}")
fi

# Ejecuta el script Python con los argumentos proporcionados
python3 hetzner_join_csv.py "${args[@]}"

# Limpia el archivo temporal
rm -f "headers_tmp.csv"

# Convierte el archivo de salida a ASCII
temp_output="${output}.tmp"
iconv -c -f utf-8 -t ascii "$output" > "$temp_output"
mv "$temp_output" "$output"

echo "El archivo ~ $output ~ ha sido guardado con éxito" 
echo "- - - - - - - -"
