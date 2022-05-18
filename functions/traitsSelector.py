import pandas as pd
import PySimpleGUI as sg
from config import *

from functions import objects


def get_NFTs_to_monitor(data, collection):
    nfts = collection.getNFTs()
    nfts_to_monitor = []
    print(data)
    # data = [objects.Trait(k, v) for k, values in data.items() for v in values if k != '#0']
    data = [objects.Trait(k, v) if k != '#0' else objects.Trait(v.split("-->")[1], v.split("-->")[0]) for k, values in data.items() for v in values]


    print(data)
    for nft in nfts:
        for trait in nft.getAttributes():
            for data_trait in data:
                # if data_trait.getTraitType() == '#0':
                #     print('gg')
                if (trait == data_trait) and (nft not in nfts_to_monitor):
                    nfts_to_monitor.append(nft)
    return nfts_to_monitor

def secondFunction_GUI(datas, collection):
    sg.set_options(auto_size_buttons=True)
    sg.theme('Black')
    layoutTables = []
    column = []
    try:
        c = 0
        for d in datas:
            tableName, df = list(d.keys())[0], list(d.values())[0]
            header_list = list(df.columns)
            data = df.values.tolist()
            if c%4 == 0:
                layoutTables.append(column)
                column = []
            column.append(
                sg.Column(
                    [
                        [sg.Text(tableName, justification="center", font=('Arial', 12,'bold')), sg.VSeparator(), sg.CB('Select all',auto_size_text=True, enable_events=True, key=f'-CHECKBOX-{c}')],
                        [sg.Table(values=data,
                            num_rows=20,
                            metadata=tableName,
                            headings=header_list,
                            display_row_numbers=True,
                            auto_size_columns=True, 
                            justification='center',
                            select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                            enable_events=True,
                            key=f'-TABLE-{c}')
                        ]
                    ]
                )
            )
            c += 1
        if len(column) != 0:
            layoutTables.append(column)
    except Exception as e:
        sg.popup_error(e)
        return

    layout = [
        layoutTables,
        [sg.HSeparator()],
        [sg.Button('Monitor',pad=(15,15), key='-MONITOR-')]
    ]
    if len(datas) > 8:
        layout = [
            [sg.Column(layoutTables, scrollable=True, vertical_scroll_only=True, size=(None, 500), expand_x=True)],
            [sg.HSeparator()],
            [sg.Button('Monitor',pad=(15,15), key='-MONITOR-')]
        ]

    window = sg.Window('NFTs Scraper', layout, grab_anywhere=False, finalize=True, resizable=True)

    user_click = True
    selected = [[] for i in range(0, c)]
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED:
            break
        if event == '-MONITOR-':
            dataIndices = {}
            data = {}

            for i in range(0, c):
                dataIndices[i] = values[f'-TABLE-{i}']

            for k, values in dataIndices.items():
                if(len(values) > 0):
                    if(k != 0):
                        data[window[f'-TABLE-{k}'].metadata] = [window[f'-TABLE-{k}'].get()[v][0] for v in values]
                    else:
                        data[window[f'-TABLE-{k}'].metadata] = [window[f'-TABLE-{k}'].get()[v][0]+'-->'+window[f'-TABLE-{k}'].get()[v][1] for v in values]
            sg.Popup('Monitor starting... the panel will close.')
            # print(data)
            nfts_to_monitor = get_NFTs_to_monitor(data, collection)
            break          
        for i in range(0, c):
            if event == f'-TABLE-{i}':
                if user_click:
                    if len(values[f'-TABLE-{i}']) == 1:
                        select = values[f'-TABLE-{i}'][0]
                        if select in selected[i]:
                            selected[i].remove(select)
                        else:
                            selected[i].append(select)
                        window[f'-TABLE-{i}'].update(select_rows=selected[i])
                        user_click = False
                else:
                    user_click = True
            if event == f'-CHECKBOX-{i}':
                if window[f'-CHECKBOX-{i}'].get():
                    selected[i] = [i for i in range(0, len(window[f'-TABLE-{i}'].get()))]
                else:
                    selected[i] = []
                window[f'-TABLE-{i}'].update(select_rows=selected[i])
    window.close()
    return nfts_to_monitor

def traitsSelector():
    collection = objects.createCollection()

    tables = []  
    first_rows = []

    with open(f'metadata/{COLLECTION_NAME}/{COLLECTION_NAME}_FetchedMetadata.txt', 'w') as f:
        for key, values in collection.getTraitTypes().items():
            values = {k: v for k, v in sorted(values.items(), key=lambda item: item[1])}
            tmpValues = []
            for name, value in values.items():
                percentage = str("%.2f" % (value/(ITEMS/100)))+' %'
                tmp = [name, value, percentage]
                tmpValues.append(tmp)
            if key != 'Trait Count':
                tmp = [tmpValues[0][0], key, tmpValues[0][2]]
                first_rows.append(tmp)
            table = pd.DataFrame(tmpValues, columns=["Values", "Amount", "Percentage"])
            f.write(f'*************************\n')
            f.write(f'\t{key}\n')
            f.write(f'*************************\n')
            f.write(f'{table}\n\n\n')
            tables.append({key: table})
    first_rows = [row for row in sorted(first_rows, key=lambda x:x[2])]
    tables.insert(0, {"#0": pd.DataFrame(first_rows, columns=["Values", "Trait", "Percentage"])})
    nfts_to_monitor = secondFunction_GUI(tables, collection)
    print('\nFinished!')
    return nfts_to_monitor

if __name__ == '__main__':
    print('The script must be launched from bot file!')
