import importlib.util
from PyQt5 import QtWidgets
import sys
import os

"""
The library is capable of converting a .py file from a window generated in
pyQt5 to a componentized application.
"""


class Pryeact:
    """
    Class used to instantiate a Pryeact object capable of componetization

    Attributes
    ----------
    app : QtWidgets.QApplication
        A pyQt5 application to launch the window
    MainWindow : QtWidgets.QMainWindow
        Main window where PyQt5 window will be loaded

    Methods
    -------
    componentize(window_name, window_path, page_name)
        Transforms the .py window into a multi-component application
    """
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()

    # example windows_name=login, window_path=pages/login.py
    def componentize(self, window_name, window_path, page_name):
        """
        Transforms the .py window into a multi-component application

        Parameters
        ----------
        window_name : str
            name of the file that contains the pyqt5 window
        window_path : str
            directory where the .py file of the window is located
        page_name : str
            pyqt5 window class name present in window_path
        """

        try:
            # carregar a tela
            global app_archive, component, path_component, atribute_line, name_path
            spec = importlib.util.spec_from_file_location(f'{window_name}', f'{window_path}')
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            create_window = getattr(foo, page_name)
            window = create_window()
            window.setupUi(self.MainWindow)

            # criar o diretorio para os componentes
            name_path = ''
            path = './'
            name_path = f'{path}{page_name}/components'
            os.makedirs(name_path)

            # criar aquivo principal
            app_archive = open(f'{path}{page_name}/app.py', 'w')

            # Criar dicionario com todos os componentes da tela e seus parametros
            window_archive = open(window_path, 'r')
            components = {}
            for line in window_archive:
                # encontrar os componentes que precisam de parametros na sua criação
                if 'retranslateUi' in line:
                    window_archive.close()
                    break
                if line.count('self') > 1 or '(MainWindow)' in line:
                    need_import = line.lstrip().replace(' = ', '.').split('.')[1]
                    imported_component = line.replace('(', '!').replace(')', '!').replace('self.', '').split('!')[1]
                    if 'QtCore.Qt' in line:
                        continue
                    elif need_import in components.keys():
                        components[need_import].append(imported_component)
                    else:
                        components[need_import] = [imported_component]

            # adicionar no dicionario de componentes aquels que nao precisam de imports
            window_archive = open(window_path, 'r')
            for line in window_archive:
                if 'retranslateUi' in line:
                    break
                elif 'self.' in line.lstrip()[:5]:
                    component = line.lstrip().replace(' = ', '.').split('.')[1]
                    if component not in components.keys():
                        components[component] = None
            window_archive.close()

            # Criar as pastas e arquivos dos componentes e fazer a base do arquivo (imports e declaracao da funcao)
            for atribute, parameters in components.items():

                # criar pasta para componente
                path_component = f'{name_path}/{atribute}'
                os.makedirs(path_component)

                # criar arquivo python com codigo do componente
                component = open(f'{path_component}/{atribute}.py', 'w')

                # criar linhas de imports e declaracao do componente em cada aquivo dos componentes
                if parameters is not None:
                    # o componente precisa de parametros para funcionar
                    all_parameters = ''
                    for index, parameter in enumerate(parameters):
                        final_index = len(parameters)
                        final_index -= 1
                        if index == final_index:
                            all_parameters += f'{parameter}'
                        else:
                            all_parameters += f'{parameter}, '
                    component.write(f'from PyQt5 import QtWidgets, QtGui, QtCore\n\n\n'
                                    f'def {atribute}({all_parameters}):\n')
                    components[atribute] = all_parameters.replace(', ', ', self.')
                else:
                    # o componente nao precisa de parametros para funcionar
                    component.write(f'from PyQt5 import QtWidgets, QtGui, QtCore\n\n\n'
                                    f'def {atribute}():\n')
                # adicionando os imports no arquivo principal (app.py)
                app_archive.write(f'from components.{atribute}.{atribute} import {atribute}\n')
                component.close()
            app_archive.write('\n\n')

            # fazer leitura do arquivo e escrever nos componentes
            window_archive = open(window_path, 'r')
            atribute_line = ''
            last_atribute = ''
            write_component = 0

            # copia do dicionario components para ser usado na declaracao dos componentes no arquivo principal
            components_declaration = components.copy()

            # Enviar os códigos para os arquivos corretamente
            for line in window_archive:
                if 'QtCore.Qt' in line:
                    app_archive.write(line)
                    continue
                # A partir do retranslateUi, todas as linhas devem ser escritas no arquivo principal
                if 'def retranslateUi' in line:
                    arquivo = open(window_path, 'r')
                    write = 0
                    for lines in arquivo:
                        if 'def retranslateUi' in lines:
                            write = 1
                        if write:
                            app_archive.write(lines)
                    break
                if 'retranslateUi' in line:
                    app_archive.write(f'{line}\n\n')

                    continue
                if 'MainWindow' in line.lstrip()[:12]:
                    app_archive.write(line)
                    continue
                # escrever a declaracao do componente no arquivo principal
                if 'self.' in line.lstrip()[:5]:
                    atribute_line = line.lstrip().replace(' = ', '.').split('.')[1]
                    if atribute_line != last_atribute:
                        last_atribute = atribute_line
                        # escrevendo no app principal a declaração do objeto com seu parâmetro
                        # isso so deve ser feito uma unica vez, portanto usarei um dicionario auxiliar e removerei
                        # os itens depois que declarados
                        if atribute_line in components_declaration.keys():
                            if components_declaration[atribute_line] is not None:
                                if 'MainWindow' in components[atribute_line] or 'statusbar' in atribute_line:
                                    app_archive.write(
                                        f'        self.{atribute_line} = {atribute_line}({components[atribute_line]})\n')
                                    if atribute_line in components_declaration.keys():
                                        del components_declaration[atribute_line]
                                else:
                                    # iterar pela lista de components e adicionar escrever aqueles que já possuem seus
                                    # parametros já declarados
                                    # continuar mexendo aqui
                                    # iterar na lista de componentes
                                    while components_declaration.keys():
                                        for componente in components.keys():
                                            if componente in components_declaration.keys():
                                                x = 0
                                                lista_parametros = []
                                                lista_parametros = components_declaration[componente].replace(', ',' ').replace('self.', '').split()

                                                for parametro in lista_parametros:
                                                    # verificar se o parametro ainda nao foi declarado no arquivo principal
                                                    if parametro not in components_declaration.keys():
                                                        x += 1
                                                if x == len(lista_parametros):
                                                    # todos os parametros já foram declarados
                                                    # declarar atributo com esses parametros
                                                    if 'MainWindow' in components[componente] or 'statusbar' in componente:
                                                        app_archive.write(
                                                            f'        self.{componente} = {componente}({components[componente]})\n')
                                                        if componente in components_declaration.keys():
                                                            del components_declaration[componente]
                                                    else:
                                                        app_archive.write(
                                                            f'        self.{componente} = {componente}(self.{components[componente]})\n')
                                                    if componente in components_declaration.keys():
                                                        del components_declaration[componente]
                            else:
                                app_archive.write(f'        self.{atribute_line} = {atribute_line}()\n')
                if ('font' in line or 'sizePolicy' in line or 'spacerItem' in line) and atribute_line:
                    component = open(f'{name_path}/{last_atribute}/{last_atribute}.py', 'a')
                    component.write(line.replace('self.', ''))
                    component.close()
                elif 'self.' in line.lstrip()[:5] and line.count('self') < 2:
                    write_component = 1
                    component = open(f'{name_path}/{atribute_line}/{atribute_line}.py', 'a')
                    component.write(line.replace('self.', ''))
                    component.close()
                elif write_component or "=" not in line and line.count('self') > 1:
                    component = open(f'{name_path}/{atribute_line}/{atribute_line}.py', 'a')
                    component.write(line.replace('self.', ''))
                    component.close()
                else:
                    write_component = 0
                    app_archive.write(line)

            # escrever os returns
            for atribute in components:
                component = open(f'{name_path}/{atribute}/{atribute}.py', 'a')
                component.write(f'        return {atribute}\n')
                component.close()
                app_archive.close()
            print(f'SUCCESS: Window created in {os.getcwd()}/{page_name}')

        except FileExistsError:
            print("ERROR: Já existe um diretorio com esse nome!")
        except FileNotFoundError:
            print('ERROR: Arquivo não encontrado!\n'
                  f'{window_path}')
        except NameError:
            print('ERROR: Arquivo .py não encontrado!\n')
