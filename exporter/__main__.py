from slugify import slugify
import PySimpleGUI as sg
import numpy as np
import csv
import re
import os

thousand_sep = ""
decimal_sep = ""

font = ('Arial', 14)

equivalences = {
    'Identificador de URL': 'Articulo',
    'Nombre': 'Articulo', 
    'Categorías': 'Rubro', 
    'Precio': 'PU', 
    'Stock': 'Existencia', 
    'SKU': '\ufeffCodigo', 
    'Descripción': 'Articulo', 
    'Tags': 'Articulo', 
    'Título para SEO': 'Articulo', 
    'Marca': 'Marca', 
    'MPN (Número de pieza del fabricante)': 'Cod. Provee'
}

def setup_window(columns=None):
    global font

    select_file = [
        [
            sg.Text("Seleccionar archivo de origen", font=font, pad=(10,10)),
            sg.In(
                size=(25, 1), 
                enable_events=True, 
                expand_x=True,
                key="-FILE-",
                font=font
            ),
            sg.FileBrowse(font=font, size=(16, 1), file_types=(('Archivo CSV', 'text/csv'),), pad=(10, 10)),
        ]        
    ]

    format_layout = [
       [
          sg.Text("Separador de miles", font=font, pad=(10, 10)),
          sg.InputText(key='-THOUSAND-SEP-', size=(4,1), enable_events=True, font=font),
          sg.Text("Separador decimal", font=font, pad=(10, 10)),
          sg.InputText(key='-DECIMAL-SEP-', size=(4,1), enable_events=True, pad=(10, 10), font=font)
       ]
    ]

    select_columns = [
    ]

    if columns:
        for i, column in enumerate(columns):
            select_columns.append([sg.Checkbox(column, 
                                               default=True, 
                                               key=f"-CHECKBOX-{i}-", 
                                               disabled=i < 4,
                                               enable_events=True,
                                               font=font)])

    layout = [
        [sg.Frame(title="Archivo de entrada:", layout=select_file, expand_x=True, font=font)],
        [sg.Frame(title="Formato de entrada:", layout=format_layout, font=font)],
        [sg.Frame(title="Columnas a incluir:", layout=select_columns, expand_x=True, font=font)],
        [sg.InputText(key='-SAVE_AS-', do_not_clear=False, enable_events=True, visible=False),
        sg.FileSaveAs(
            font=font,
            button_text='Generar y guardar',
            pad=(5, 15),
            size=(25, 1),
            default_extension=".csv",
            file_types=(('Archivo CSV', '.csv'),),
        )]        
    ]

    window = sg.Window("Generador de archivo p/ Importación", 
                       layout=layout, 
                       size=(800,540),
                       location=(0, 0))

    return window

def read_csv_file(filepath, delimiter=",", include_header=True):
  input_headers = []
  input_rows = []

  with open(filepath) as csvfile:
    csvreader = csv.reader(csvfile, delimiter=delimiter)
    for i, row in enumerate(csvreader):
      if row[0] == "": break
      if include_header and i == 0:
        input_headers = row[:]
        continue
      input_rows.append(row[:])

  return (input_headers, input_rows)

def extract_brands() -> str:
  brands_list = []

  path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'marcas.csv'))

  with open(path) as brandscsv:
    csvreader = csv.reader(brandscsv, delimiter=',')
    for i, row in enumerate(csvreader):
      if i == 0: continue
      if row[0] == '': break
      brands_list.append(row[0])

  brands_set = set(brands_list)

  return '|'.join(map(re.escape, brands_set))

def write_csv_file(output_path: str, input_rows, input_headers, output_headers, brands: str, delimiter=","):
  
  global equivalences
  
  with open(output_path, 'w', newline='') as outputfile:
    writer = csv.writer(outputfile, delimiter=delimiter)
    writer.writerow(output_headers)    
    for input_row in input_rows:
        
        stock = input_row[input_headers.index("Existencia")]
        if stock == "":
           continue
        
        row = []
        
        for i, col_name in enumerate(output_headers):
            input_name = equivalences[col_name]
            input_value = input_row[input_headers.index(input_name)]

            if col_name == 'Identificador de URL':
                input_value = slugify(input_value)
            elif col_name == 'Precio':
                input_value = input_value.replace(thousand_sep, "").replace(f"{decimal_sep}", ".")
            elif col_name == 'Stock':
                input_value = input_value.replace(thousand_sep, "").replace(f"{decimal_sep}00", "")                
                input_value = input_value if float(input_value) >= 0 else 0 
            elif col_name == 'SKU':
                input_value = input_value.replace(thousand_sep, "").replace(f"{decimal_sep}00", "")
            elif col_name == 'MPN (Número de pieza del fabricante)':
                input_value = input_value.replace(thousand_sep, "")
            elif col_name == 'Marca':
                name = input_row[input_headers.index("Articulo")]
                search_r = re.search(fr'\b({brands})\b', name)
                input_value = search_r.group().strip() if search_r else "SIN MARCA"


            row.append(input_value)
        
        writer.writerow(row)

def detect_delimiter(csv_file):
    with open(csv_file, 'r') as my_csv:
        header = my_csv.readline()
        if header.find(";")!=-1:
            return ";"
        if header.find(",")!=-1:
            return ","

    return ";"

def main():
    
    global thousand_sep
    global decimal_sep

    brands = extract_brands() 

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'template.csv'))

    delimiter = detect_delimiter(path)

    template_cols, _ = read_csv_file(path, include_header=True, delimiter=delimiter)

    selected_cols = template_cols.copy()

    window = setup_window(template_cols)

    input_path = None

    # Run the Event Loop
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # Folder name was filled in, make a list of files in the folder
        elif event == "-FILE-" and values["-FILE-"] != '':
            input_path = values["-FILE-"]
        elif "-CHECKBOX-" in event:
            values = list(dict(filter(lambda p: "-CHECKBOX-" in p[0], values.items())).values())
            selected_cols = np.array(template_cols)[values]
        elif event == "-THOUSAND-SEP-":
           thousand_sep=values["-THOUSAND-SEP-"]
        elif event == "-DECIMAL-SEP-":
            decimal_sep=values["-DECIMAL-SEP-"]
        elif event == "-SAVE_AS-":
            if thousand_sep not in (",",".") or decimal_sep not in (",",".") or thousand_sep == decimal_sep:
                sg.popup_error(f"Formato para separador de miles y/o separador decimal incorrecto", 
                    title="No se pudo generar el archivo",
                    font=font,
                    auto_close=True,
                    auto_close_duration=5000,
                    keep_on_top=True)
                continue
            if not input_path or input_path == "":
                sg.popup_error(f"No se seleccionó el archivo de origen", 
                    title="No se pudo generar el archivo",
                    font=font,
                    auto_close=True,
                    auto_close_duration=5000,
                    keep_on_top=True)
                continue

            output_path = values["-SAVE_AS-"]   

            delimiter = detect_delimiter(input_path)

            cols, rows = read_csv_file(input_path, delimiter=delimiter)   
            
            try:
                write_csv_file(
                    output_path=output_path, 
                    input_rows=rows,
                    input_headers=cols,
                    output_headers=selected_cols,
                    brands=brands
                )
                sg.popup("Archivo guardado exitosamente",
                        title="Guardado",
                        font=font)
            except ValueError as ve:
                sg.popup_error(f"Información del error: {ve}", 
                            title="No se pudo generar el archivo",
                            font=font,
                            auto_close=True,
                            auto_close_duration=5000,
                            keep_on_top=True)    

    window.close()

if __name__ == "__main__":
   main()