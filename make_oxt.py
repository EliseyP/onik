# _*_ coding: utf-8

"""
Сборка oxt расширения для случаев без изменений в GUI.
Основа берется из имеющегося последнего собранного oxt.
Заменяются файлы модулей из py, py/pythonpath.

Для сборки при изменениях в GUI а также в макросах LO,
коректнее (на данный момент) пересобрать с помощью LO-компилятора.

Из файла update считывается текущая версия расширения.
Запускается диалог ввода новой версии.
Файлы oxt и update копируются во временный каталог 1.
Внутри временного каталога 1:
    В update файле меняется номер версии.
    Oxt распаковывается во временный каталог 2.
    Внутри временного каталога 2:
        Каталог py копируется из src/OOnik
        Удаляется __pycache__
        В description файле меняется номер версии.
    Oxt переупаковывается.
oxt и update файлы в scr/OOnik и в текущем каталоге заменяются обновленными.
"""

import os
import shutil
import tempfile
from pathlib import Path
from zipfile import ZipFile
from distutils.dir_util import copy_tree
from packaging import version
from utils.breezypythongui import EasyFrame


class MsgTk(EasyFrame):
    def __init__(self, _title='OXT compiler', _string=None, _w=40):
        EasyFrame.__init__(self)
        root = self.master
        root.withdraw()
        self.messageBox(title=_title, message=_string, width=_w)
        root.destroy()


class PromtTk(EasyFrame):
    def __init__(self, _title='OXT compiler', _string='1.1.92', _w=20):
        EasyFrame.__init__(self)
        root = self.master
        root.withdraw()
        self.value = self.prompterBox(title=_title, promptString='Version', inputText=_string, fieldWidth=_w)
        root.destroy()

    def get_value(self):
        return self.value


# Версия (last = 1.1.94)
class Version:
    MAJOR: int = 1
    MINOR: int = 1
    MICRO: int = 94

    def __str__(self):
        return f"{self.MAJOR}.{self.MINOR}.{self.MICRO}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if (self.MAJOR == int(other.MAJOR)
                and self.MINOR == int(other.MINOR)
                and self.MICRO == int(other.MICRO)):
            return True
        else:
            return False

    def __lt__(self, other):
        if version.parse(str(self)) < version.parse(str(other)):
            return True
        else:
            return False

    def __gt__(self, other):
        if version.parse(str(self)) > version.parse(str(other)):
            return True
        else:
            return False


class MyError(Exception):
    """Общий класс ошибок"""


class MyErrorNoArgs(MyError):
    """Нет аргументов"""


class MyErrorNoArgsNone(MyErrorNoArgs):
    """Нет аргументов - None"""
    def __init__(self, message=''):
        _out_string = ''
        if message:
            _out_string = f'{message}: '
        self.message = f'{_out_string}Arg is None!'
        super().__init__(self.message)


class MyErrorNoArgsEmpty(MyErrorNoArgs):
    """Нет аргументов - Empty"""
    def __init__(self, message='', _type: str = None):
        if not message:
            message = ''
        if not _type:
            _type = ''
        _out_string = ''
        _type_str = ''
        if _type:
            _type_str = f' ({_type})'
        if message:
            _out_string = f'{message}: '
        self.message = f'{_out_string}Arg{_type_str} is Empty!'
        super().__init__(self.message)


class MyErrorOperation(MyError):
    """Неудачное выполнение операции"""


def check_args_handler(_args_list=None, _type_out='', _string=''):
    # Raise or return if one arg is None or Emty
    if _args_list is None:
        _args_list = []
    assert _args_list, f'Invalid usage: no arg list for checking!'
    if _string is None:
        _string = ''
    for _arg in _args_list:
        _type = type(_arg)
        if _arg is None:
            if _type_out == 'return':
                return False
            elif _type_out == 'raise':
                raise MyErrorNoArgsNone(_string)
        elif (_type is str and _arg == '') or \
                (_type is list and _arg == []) or \
                (_type is tuple and _arg == ()) or \
                (_type is dict and _arg == {}) or \
                (_type is set and _arg == set()):
            if _type_out == 'return':
                return False
            elif _type_out == 'raise':
                raise MyErrorNoArgsEmpty(_string, _type.__name__)
    return True


def check_args_and_raise(_args_list=None, _string=''):
    """Проверка аргументов и Raise if one arg is None or Empty.

    :param _args_list: спикок аргументов для проверки.
    :param _string: строка для вывода.
    """
    assert _args_list, f'check_args_and_raise: Invalid usage: no arg list for checking!'
    check_args_handler(_args_list=_args_list, _string=_string, _type_out='raise')


def regex_sub_in_whole_txt_file(_file: str = None, _regs_list=None, _search='', _replace='', _flags=0, _amount=0):
    """Поиск и замена (regex) в текстовом файле (in-place)

    :param _file: Путь к файлу
    :param _regs_list: Список рег.выр-й
    :param _search: Выражение поиска (r'\\d')
    :param _replace: Выражение замены
    :param _flags: строка флагов 'mxsu'
    :param _amount: int, def=0
    :return:
    """
    debh = 'regex_sub_in_whole_txt_file'
    check_args_and_raise([_file], f'{debh}')

    import re
    import functools
    import operator

    if _regs_list is None:
        _regs_list = []

    def string_to_rflags(_flags_str):
        """Переводит строку re-флагов 'mxs' в число, соответствующее сумме re-флагов

        :param _flags_str: Строка флагов
        :return: Сумма
        """

        def flags_summing(_flags_list) -> int:
            return functools.reduce(operator.or_, _flags_list)

        flags_list = []
        # Составление списка флагов из строки
        if _flags_str != 0 and type(_flags_str) is str:
            if 'u' in _flags_str:
                flags_list.append(re.U)
            if 'x' in _flags_str:
                flags_list.append(re.X)
            if 'm' in _flags_str:
                flags_list.append(re.M)
            if 's' in _flags_str:
                flags_list.append(re.S)

            _rflags = flags_summing(flags_list)
            return _rflags
        else:
            return None

    # Read in the file
    try:
        with open(_file, encoding='utf-8', mode='r') as file:
            filedata = file.read()
    except Exception as er:
        raise MyErrorOperation(f'{debh}: Error open {_file}! {er}')

    _regs_list_inner = []
    if not _regs_list:
        _regs_list_inner.append([_search, _replace, _flags, _amount])
    else:
        _regs_list_inner = _regs_list

    for _reg_rec in _regs_list_inner:
        _search_str = ''
        _replace_str = ''
        _flags_str_or_int = 0  # используется как временное хранилище для строки флагов если она задана в списке.
        _flags_rflags = 0  # будет передан как флаг в re.compile
        _amount_int = 0
        _len_of_rec = len(_reg_rec)

        if _len_of_rec == 2:
            _search_str, _replace_str = _reg_rec
        elif _len_of_rec == 3:
            _search_str, _replace_str, _flags_str_or_int = _reg_rec
        elif _len_of_rec == 4:
            _search_str, _replace_str, _flags_str_or_int, _amount_int = _reg_rec

        if type(_flags_str_or_int) is str:
            _flags_rflags = string_to_rflags(_flags_str_or_int)
        elif type(_flags_str_or_int) is int:
            _flags_rflags = _flags_str_or_int

        try:
            # rx объект с учетом флагов.
            re_obj = re.compile(_search_str, flags=_flags_rflags)
        except (TypeError, AttributeError, re.error) as er:
            raise MyErrorOperation(f'{debh}: Ошибка компиляции regex-шаблона! {er}')

        # Замена
        filedata = re_obj.sub(_replace_str, filedata, _amount_int)

    # Применить изменения.
    try:
        with open(_file, encoding='utf-8', mode='w') as file:
            file.write(filedata)

    except Exception:
        raise MyErrorOperation(f'{debh}: Error open and write to file: {_file}!')

    return None


def get_version_from_current_update_file(_file: str = None, _search: str = None):
    import re
    _version = Version()
    if _file is None or _search is None:
        return
    with open(_file) as f:
        for line in f:
            match = re.search(_search, line.rstrip())
            if match:
                _version.MAJOR = match.group(1)
                _version.MINOR = match.group(2)
                _version.MICRO = match.group(3)
                return _version
    return version_default


cwd = os.getcwd()
p_cwd = Path(cwd)
p_onik_dir = p_cwd.joinpath('src/OOnik')
OXT_FILE_NAME = 'OOnik.oxt'
p_oxt_path = p_onik_dir.joinpath(OXT_FILE_NAME)
p_oxt_path_new = p_onik_dir.joinpath(f'_{OXT_FILE_NAME}')
p_oxt_path_bck = p_onik_dir.joinpath(f'{OXT_FILE_NAME}~')
UPDATE_FILE_NAME = 'OOnik-L.update.xml'
p_update_path = p_onik_dir.joinpath(UPDATE_FILE_NAME)
p_update_path_bck = p_onik_dir.joinpath(f'{UPDATE_FILE_NAME}~')
p_update_path_new = p_onik_dir.joinpath(f'_{UPDATE_FILE_NAME}')
version_default = Version()
DESCRIPTION_FILE_NAME = 'description.xml'
dir_for_unzip = 'tmp_dir'

regex_str = r'version\ value=\"(\d+)\.(\d+)\.(\d+)\"'


def main():
    # Определить номер версии, собранной в src/OOnik/OOnik-L.update.xml.
    version_in_update = \
        get_version_from_current_update_file(p_update_path.as_posix(), regex_str)
    print(f'New version: {version_in_update}')

    def get_version_new() -> Version:
        promt = PromtTk(_string=str(version_in_update))
        version_new_raw = promt.get_value()
        version_new_l = version_new_raw.split('.')
        _version_new = Version()
        if not all([str(x).isdigit() for x in version_new_l]):
            print(f'[!] Некорректный формат: {version_new_raw}')
            raise MyErrorOperation(f'Некорректный формат: {version_new_raw}')
        else:
            try:
                version_new_l = [int(x) for x in version_new_l]
            except ValueError as err:
                print(f'[!] Ошибка формата. Выход. {err}')
                raise MyErrorOperation(f'Ошибка формата! {err}')

        _version_new.MAJOR, _version_new.MINOR, _version_new.MICRO = version_new_l
        return _version_new

    def check_version_new():
        if version_new < version_in_update:
            print(f'[!] Версия "{version_new}" меньше исходной "{version_in_update}"!')
            raise MyErrorOperation(
                f'Версия "{version_new}" меньше исходной "{version_in_update}"!')

    def get_new_oxt_and_update_files():
        # Получить обновленные файлы oxt и update и скопировать их в src/OOnik
        with tempfile.TemporaryDirectory() as tmpdirname:

            p_update_file_tmp = Path(tmpdirname).joinpath(UPDATE_FILE_NAME)
            p_oxt_file_tmp = Path(tmpdirname).joinpath(OXT_FILE_NAME)
            p_oxt_file_tmp_new = Path(tmpdirname).joinpath(f'_{OXT_FILE_NAME}')
            p_oxt_file_tmp_new_zipped = p_oxt_file_tmp_new.with_suffix('.oxt.zip')

            python_dir_name = 'py'
            p_python_dir = p_onik_dir.joinpath(python_dir_name)
            p_python_dir_tmp = Path(dir_for_unzip).joinpath(python_dir_name)
            p_pycache_dir_tmp = p_python_dir_tmp.joinpath('pythonpath/__pycache__')
            p_description_file_tmp = Path(dir_for_unzip).joinpath(DESCRIPTION_FILE_NAME)
            # images_dir_name = 'Images'
            # p_images_dir = p_onik_dir.joinpath(images_dir_name)
            # oonik_dir_name = 'OOnik'
            # p_oonik_dir = p_onik_dir.joinpath(oonik_dir_name)

            _regs = [[regex_str, f'version value="{version_new}"', 'u']]

            def copy_update_to_tmp():
                try:
                    print('Copy update to tmp ... ', end='')
                    shutil.copy2(p_update_path, p_update_file_tmp)
                except OSError as err:
                    print('NO')
                    raise MyErrorOperation from err
                else:
                    print('OK')

            def copy_oxt_to_tmp():
                try:
                    print('Copy oxt to tmp ... ', end='')
                    shutil.copy2(p_oxt_path, p_oxt_file_tmp)
                except OSError as err:
                    print('NO')
                    raise MyErrorOperation from err
                else:
                    print('OK')

            def update_version_in_xml_file(_p_file, _log_string):
                # Process file - search and replace
                try:
                    print(f'Set version in {_log_string} file ... ', end='')
                    regex_sub_in_whole_txt_file(
                        _file=_p_file.as_posix(),
                        _regs_list=_regs
                    )
                except MyError as err:
                    print('NO')
                    raise MyErrorOperation from err
                else:
                    print('OK')

            def copy_update_to_scr():
                try:
                    print(f'Copy update to scr ... ', end='')
                    shutil.copy2(p_update_file_tmp, p_update_path_new)
                except OSError as err:
                    print('NO')
                    raise MyErrorOperation from err
                else:
                    print('OK')

            def unpack_oxt():
                # Распаковка oxt во временный каталог.
                try:
                    print(f'Unpack oxt ... ', end='')
                    with ZipFile(p_oxt_file_tmp.as_posix()) as _zip:
                        _zip.extractall(dir_for_unzip)
                except OSError as err:
                    print('NO')
                    raise MyErrorOperation from err
                else:
                    print('OK')

            def copy_dir_from_src(_dir, _log_string):
                # Copy src dir from src/OOnik
                try:
                    print(f'Copy "{_log_string}" dir ... ', end='')
                    copy_tree(_dir.as_posix(), p_python_dir_tmp.as_posix())
                except EOFError as err:
                    raise MyErrorOperation from err
                else:
                    print('OK')

            def delete_pycache():
                # Delete py/pythonpath/__pycache__
                try:
                    print(f'Delete __pycache__ ... ', end='')
                    shutil.rmtree(p_pycache_dir_tmp)
                except OSError as err:
                    print('NO')
                    raise MyErrorOperation from err
                else:
                    print('OK')

            def zip_tmp_dir():
                # Архивирование измененной структуры файлов в oxt_new.
                try:
                    print(f'Zip tmp dir ... ', end='')
                    shutil.make_archive(p_oxt_file_tmp_new.as_posix(), 'zip', dir_for_unzip)
                except Exception as err:
                    print('NO')
                    raise MyErrorOperation from err
                else:
                    print('OK')

            def remove_zip_suffix_from_new_oxt_file_name():
                # Удаление суффикса .zip
                try:
                    print(f'Rename oxt ... ', end='')
                    p_oxt_file_tmp_new_zipped.rename(p_oxt_file_tmp_new)
                except OSError as err:
                    print('NO')
                    raise MyErrorOperation from err
                else:
                    print('OK')

            def copy_oxt_to_scr():
                try:
                    print(f'Copy oxt to scr ... ', end='')
                    shutil.copy2(p_oxt_file_tmp_new, p_oxt_path_new)
                except OSError as err:
                    print('NO')
                    raise MyErrorOperation from err
                else:
                    print('OK')

            copy_update_to_tmp()
            copy_oxt_to_tmp()

            # Process update file
            update_version_in_xml_file(p_update_file_tmp, 'Update')

            copy_update_to_scr()

            unpack_oxt()

            # Process files and dirs from oxt. And repack archive.
            update_version_in_xml_file(p_description_file_tmp, 'description')

            # Copy py from src/OOnik
            copy_dir_from_src(p_python_dir, 'py')
            # If need, copy other dirs from src (Images, OOnik, )
            # copy_dir_from_src(p_images_dir, 'Images')
            # copy_dir_from_src(p_oonik_dir, 'OOnik')

            delete_pycache()
            zip_tmp_dir()
            remove_zip_suffix_from_new_oxt_file_name()
            copy_oxt_to_scr()

    def bckup_orig_oxt():
        try:
            print(f'Bckup orig oxt to .oxt~ ... ', end='')
            p_oxt_path.rename(p_oxt_path_bck)
        except OSError as err:
            print('NO')
            raise MyErrorOperation from err
        else:
            print('OK')

    def rename_new_oxt():
        try:
            print(f'Rename new oxt ... ', end='')
            p_oxt_path_new.rename(p_oxt_path)
        except OSError as err:
            print('NO')
            raise MyErrorOperation from err
        else:
            print('OK')

    def delete_oxt_bck():
        try:
            print(f'Delete oxt bck ... ', end='')
            p_oxt_path_bck.unlink()
        except Exception as err:
            print('NO')
            raise MyErrorOperation from err
        else:
            print('OK')

    def bckup_orig_update():
        try:
            print(f'Bckup orig update to .xml~ ... ', end='')
            p_update_path.rename(p_update_path_bck)
        except OSError as err:
            print(f'NO')
            raise MyErrorOperation from err
        else:
            print('OK')

    def rename_new_update():
        try:
            print(f'Rename new update ... ', end='')
            p_update_path_new.rename(p_update_path)
        except OSError as err:
            print('NO')
            raise MyErrorOperation from err
        else:
            print('OK')

    def delete_update_bck():
        try:
            print(f'Delete update bck ... ', end='')
            p_update_path_bck.unlink()
        except Exception as err:
            print('NO')
            raise MyErrorOperation from err
        else:
            print('OK')

    def copy_to_cwd(_file, _log_string):
        try:
            print(f'Copy {_log_string} to cwd ... ', end='')
            shutil.copy2(p_oxt_path, cwd)
        except OSError as er:
            print('NO')
            raise MyErrorOperation from er
        else:
            print('OK')

    def delete_unzip_tmp_dir():
        # Удаление unzip каталога для oxt.
        try:
            print(f'Delete unzip tmp dir ... ', end='')
            shutil.rmtree(Path(dir_for_unzip))
        except OSError as err:
            print('NO')
            raise MyErrorOperation from err
        else:
            print('OK')

    version_new = get_version_new()
    check_version_new()

    get_new_oxt_and_update_files()

    # Replace oxt file with updated.
    bckup_orig_oxt()
    rename_new_oxt()
    delete_oxt_bck()

    # Replace update file with updated.
    bckup_orig_update()
    rename_new_update()
    delete_update_bck()

    # Копирование oxt и update в cwd.
    copy_to_cwd(p_oxt_path, 'oxt')
    copy_to_cwd(p_update_path, 'update')

    delete_unzip_tmp_dir()


if __name__ == '__main__':
    try:
        main()
    except MyError as e:
        print(f'{e}')
        MsgTk(_string=f'Ошибка!\n{e}')
    else:
        print(f'Done!')
        MsgTk(_string=f'Ok!')
