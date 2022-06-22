#!/bin/bash
# oxt_handler.sh
# Обрабатывает OxtName-L-ver.oxt
# Удаляет суффиксы '-L-ver' 
# - в имени oxt файла
# - в самом oxt в файле AddonUI.xcu 
# - в файле upd
# filename-L-ver.oxt -> filename.oxt

# Требуется zip, unzip
if ! command -v zip &> /dev/null; then
    echo "Can't find zip command"
    exit 1
fi

if ! command -v unzip &> /dev/null; then
   echo "Can't find unzip command"
   exit 1
fi

if [[ $# -ne 1 ]] ; then
    echo "No parameters!"
    exit 1
else 
    OXT_SRC=$1
fi


CURR_DIR="$PWD"
NAME_LIB=`echo "$OXT_SRC" | sed -re "s/(^.*)-L-[0-9]+\.[0-9]+\.[0-9]+\.oxt/\1/"`
NAME_OXT="${NAME_LIB}.oxt"
UPD_FILE="${NAME_LIB}-L.update.xml"
ADDON_FILE="AddonUI.xcu"
TMP_DIR=$(mktemp -d /tmp/_oxt_handler.$$.1.XXXXXXXXXX)

[[ -e "$OXT_SRC" ]] || exit 1

# Обработка upd file
sed -i -re "s/(\/$NAME_LIB)-L-[0-9]+\.[0-9]+\.[0-9]+(\.oxt)/\1\2/" "$UPD_FILE"
# Распаковать oxt во временный каталог
unzip -oqq "${OXT_SRC}" -d "${TMP_DIR}"
# Внести исправления
cd "${TMP_DIR}"
if [[ -e "${ADDON_FILE}" ]]; then
    sed -i -re "s/($NAME_LIB)-L-[0-9]+\.[0-9]+\.[0-9]+(\.oxt)/\1\2/" "${ADDON_FILE}"
fi
# Запаковать в новый oxt file
zip -rqq "${NAME_OXT}" * 

if [[ $? -eq 0 ]]; then 
    if [[ -e "${NAME_OXT}" ]]; then
        mv "${NAME_OXT}" "${CURR_DIR}"
    fi

    echo "Done. ${NAME_OXT} is available."
else
    echo "Ошибка. Bye!"
    exit 1
fi

exit 0



