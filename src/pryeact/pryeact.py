import importlib.util
from PyQt5 import QtWidgets
import sys
import os


class Pryeact:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()

    # example windows_name=login, window_path=pages/login.py
    def componentize(self, window_name, window_path, page_name):
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
            name_path = f'{path}{page_name}'
            os.makedirs(name_path)

            # criar aquivo principal
            app_archive = open(f'{name_path}/app.py', 'w')

            # SEQUENCIA DE ETAPAS
            # CRIAR AS PASTAS
            # IDENTIFICAR NOS ATRIBUTOS AQUELES QUE PRECISAM RECEBER PARÂMETRO - feito
            # CRIAR O 'def' DE CADA COMPONENTE
            # ENVIAR AS LINHAS PARA CADA COMPONENTE
            # CRIAR A DEFINIÇÃO DE CADA COMPONENTE
            # CRIAR O RETURN DE TODOS

            # descobrir quais atributos precisam de imports para criar os paramêtros
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
                    if 'QtCore.Qt.AlignHCenter' in line:
                        continue
                    elif need_import in components.keys():
                        components[need_import].append(imported_component)
                    else:
                        components[need_import] = [imported_component]

            window_archive = open(window_path, 'r')
            for line in window_archive:
                if 'retranslateUi' in line:
                    break
                elif 'self.' in line.lstrip()[:5]:
                    print(line)
                    component = line.lstrip().replace(' = ', '.').split('.')[1]
                    if component not in components.keys():
                        components[component] = None
            window_archive.close()

            for atribute, parameters in components.items():
                # criar pasta para componente e criar componente
                path_component = f'{name_path}/{atribute}'
                os.makedirs(path_component)

                # criar arquivo python com codigo do componente
                component = open(f'{path_component}/{atribute}.py', 'w')

                if parameters is not None:
                    # tem parametro
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
                    component.write(f'from PyQt5 import QtWidgets, QtGui, QtCore\n\n\n'
                                    f'def {atribute}():\n')
                # adicionando os imports no arquivo principal (app.py)
                app_archive.write(f'from {atribute}.{atribute} import {atribute}\n')
                component.close()

            app_archive.write('\n\n')
            # fazer leitura do arquivo e escrever nos componentes

            ''' --------------------------------------------------------------------------'''

            window_archive = open(window_path, 'r')
            atribute_line = ''
            last_atribute = ''
            write_component = 0

            # copia do dicionario components para ser usado na declaracao dos componentes no arquivo principal
            components_declaration = components.copy()
            # Enviar os códigos para os arquivos corretamente
            for line in window_archive:
                # a partir do retranslateUi, todas as linhas devem ser escritas no arquivo principal

                # condição especifica
                if 'QtCore.Qt.AlignHCenter' in line:
                    app_archive.write(line)
                    continue
                if 'retranslateUi' in line:
                    for line in window_archive:
                        app_archive.write(line)
                    break
                if 'MainWindow' in line.lstrip()[:12]:
                    app_archive.write(line)
                    continue
                # escrever a declaracao do componente no arquivo principal
                if 'self.' in line.lstrip()[:5]:
                    print("entrei - 0")
                    print(line)
                    atribute_line = line.lstrip().replace(' = ', '.').split('.')[1]
                    if atribute_line != last_atribute:
                        last_atribute = atribute_line
                        # escrevendo no app principal a declaração do objeto com seu parâmetro
                        # isso so deve ser feito uma unica vez, portanto usarei um dicionario auxiliar e removerei
                        # os itens depois que declarados
                        if atribute_line in components_declaration.keys():
                            if components_declaration[atribute_line] is not None:
                                if 'MainWindow' in components[atribute_line] and 'centralwidget' in atribute_line or 'statusbar' in atribute_line:
                                    app_archive.write(
                                        f'        self.{atribute_line} = {atribute_line}({components[atribute_line]})\n')
                                else:
                                    app_archive.write(f'        self.{atribute_line} = {atribute_line}(self.{components[atribute_line]})\n')
                            else:
                                app_archive.write(f'        self.{atribute_line} = {atribute_line}()\n')
                            del components_declaration[atribute_line]
                # melhorar ds daqui
                if ('font' in line or 'sizePolicy' in line or 'spacerItem' in line) and atribute_line:
                    print("entrei - 1")
                    print(line)
                    component = open(f'{name_path}/{last_atribute}/{last_atribute}.py', 'a')
                    component.write(line.replace('self.', ''))
                    component.close()
                elif 'self.' in line.lstrip()[:5] and line.count('self') < 2:
                    print("entrei - 2")
                    print(line)
                    write_component = 1
                    component = open(f'{name_path}/{atribute_line}/{atribute_line}.py', 'a')
                    component.write(line.replace('self.', ''))
                    component.close()
                elif write_component or "=" not in line and line.count('self') > 1:
                    print("entrei - 3")
                    print(line)
                    component = open(f'{name_path}/{atribute_line}/{atribute_line}.py', 'a')
                    component.write(line.replace('self.', ''))
                    component.close()
                else:
                    # essa linha possui um novo atributo
                    print("entrei - 4")
                    print(line)
                    write_component = 0
                    app_archive.write(line)
        except FileExistsError:
            # perguntar ao usuário se renomeia ou ignora
            pass
        #except FileNotFoundError:
            #print('Diretório não existente')
        except NameError:
            pass


tela = Pryeact()
tela.componentize('login', 'pages/login.py', 'login')
