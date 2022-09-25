import importlib.util
from PyQt5 import QtWidgets
import sys
import os

# transformará um arquivo .py gerado pela conversão do QT design em uma tela com seus itens componentizados
class Pryeact:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()

    # example windows_name=login, window_path=pages/login.py
    def componentize(self, window_name, window_path):
        # carregar a tela
        global app_archive, component, path_component, atribute_line
        spec = importlib.util.spec_from_file_location(f'{window_name}', f'{window_path}')
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        window = foo.Ui_MainWindow()
        window.setupUi(self.MainWindow)
        # carregar os atributos
        atributes = list(window.__dict__.keys())

        # criar pasta para a tela no diretorio atual
        # recebe um caminho
        name_path = ''
        try:
            path = './'
            name_path = f'{path}/window'
            os.makedirs(name_path)

            # criar aquivo principal
            app_archive = open(f'{name_path}/app.py', 'w')

            # escreves todos os imports no arquivo principal (app.py)
            for atribute in atributes:
                # criar pasta para componente e criar componente
                path_component = f'{name_path}/{atribute}'
                os.makedirs(path_component)

                # criar arquivo python com codigo do componente
                component = open(f'{path_component}/{atribute}.py', 'w')

                # escrever base do componente
                component.write(f'from PyQt5 import QtWidgets, QtGui\n\n\n'
                                f'def {atribute}():\n')

                # adicionando os imports no arquivo principal (app.py)
                app_archive.write(f'from {atribute}.{atribute} import {atribute}\n')

            app_archive.write('\n\n')

            # fazer leitura do arquivo e escrever nos componentes
            window_archive = open(window_path, 'r')
            write_component = 0
            atribute_line = ''
            last_atribute = ''

            for line in window_archive:
                if 'retranslateUi' in line:
                    for line in window_archive:
                        app_archive.write(line)
                    break
                if 'self.' in line.lstrip()[:5]:
                    atribute_line = line.lstrip().replace(' = ', '.').split('.')[1]
                    if atribute_line != last_atribute and atribute_line != 'font' and atribute_line != 'sizePolicy':
                        last_atribute = atribute_line
                        app_archive.write(f'        self.{atribute_line} = {atribute_line}()\n')
                if 'font' in line or 'sizePolicy' in line or 'spacerItem' in line:
                    component = open(f'{name_path}/{last_atribute}/{last_atribute}.py', 'a')
                    component.write(line.replace('self.', ''))
                    component.close()
                elif 'self.' in line.lstrip()[:5] and line.count('self') < 2:
                    print('entrei na 0')
                    print(line)
                    # descobrir qual o componente
                    write_component = 1
                    component = open(f'{name_path}/{atribute_line}/{atribute_line}.py', 'a')
                    component.write(line.replace('self.', ''))
                    component.close()
                elif write_component and "=" not in line and line.count('self') < 2:
                    print("entrei - 2")
                    print(line)
                    component = open(f'{name_path}/{atribute_line}/{atribute_line}.py', 'a')
                    component.write(line.replace('self.', ''))
                    component.close()
                else:
                    # essa linha possui um novo atributo
                    print("entrei - 3")
                    print(line)
                    write_component = 0
                    app_archive.write(line)
        except FileExistsError:
            # perguntar ao usuário se renomeia ou ignora
            pass
        except FileNotFoundError:
            print('Diretório não existente')
        except NameError:
            pass
