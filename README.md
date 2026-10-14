<h1 align="center">
  Bitwarden Item Cleaner 📄

  [RUS](#rus) // [ENG](#eng)
</h1>

<h1 align="center">
  <a id="rus" href="#rus"><b>RUS</b></a>
</h1>


## Зачем нужен этот скрипт?

При использовании Bitwarden можно случайно открыть устаревшую ссылку из сохраненного элемента — например, старую страницу восстановления пароля. Из-за этого приходится вручную возвращаться на сайт, находить форму входа и заново вводить данные.

Скрипт помогает поддерживать ссылки в хранилище в аккуратном и предсказуемом виде: он может оставить только домен или поддомен, убрать старую историю паролей и обработать сразу весь экспорт. Это удобно перед импортом хранилища обратно в Bitwarden, особенно если в нем много элементов.

## Возможности

- ### Нормализация URI

  Скрипт поддерживает два режима преобразования веб-ссылок. Флаги `--domain` и `--subdomain` взаимоисключающие. Обрабатываются URI без схемы, а также URI со схемами `http` и `https`; остальные URI пропускаются.

  #### 1. Только домен

  Оставляет в URI домен верхнего уровня и добавляет завершающий `/`.

  ```bash
  python bwc.py bitwarden_export.json --domain
  ```

  Короткая форма: `-dom`.

  ![](https://github.com/graythze/BitwardenItemCleaner/blob/main/src/pic/domain.jpg)

  #### 2. Домен вместе с поддоменом

  Сохраняет поддомен, домен и публичный суффикс.

  ```bash
  python bwc.py bitwarden_export.json --subdomain
  ```

  Короткая форма: `-subd`.

  ![](https://github.com/graythze/BitwardenItemCleaner/blob/main/src/pic/subdomain.jpg)

- ### Очистка истории паролей

  Флаг `--rmusedpws` очищает поле `passwordHistory` у элементов типа «логин». Старые ранее использованные пароли удаляются из результата.

  ```bash
  python bwc.py bitwarden_export.json --rmusedpws
  ```

  Короткая форма: `-rmpw`.

  ![](https://github.com/graythze/BitwardenItemCleaner/blob/main/src/pic/removeusedpw.jpg)

- ### Совместное использование

  Флаги очистки истории паролей и нормализации URI можно использовать одновременно:

  ```bash
  python bwc.py bitwarden_export.json --domain --rmusedpws
  python bwc.py bitwarden_export.json --subdomain --rmusedpws
  ```

- ### Дополнительные параметры

  - `--bypassip` (`-byp`) не изменяет URI, содержащие IPv4- или IPv6-адреса. Без этого флага IP-адрес сохраняется, но нормализуется и получает завершающий `/`.
  - `--getpsl` (`-psl`) разрешает загрузить Public Suffix List из сети. Без флага скрипт работает офлайн и использует `tldextract` без сетевого запроса.

## Установка

Требуется Python 3 и зависимость `tldextract`:

```bash
python -m pip install -r requirements.txt
```

## Использование

Первым аргументом передается путь к JSON-файлу экспорта Bitwarden:

```bash
python bwc.py <path-to-bitwarden-export.json> [options]
```

Примеры:

```bash
python bwc.py vault.json --domain
python bwc.py vault.json --subdomain --bypassip
python bwc.py vault.json --rmusedpws
python bwc.py vault.json --domain --getpsl
```

Если не указать `--domain` или `--subdomain`, URI не изменяются. При этом `--rmusedpws` можно использовать отдельно.

После выполнения скрипт создает файл с именем вида `bw_cleaned<timestamp>.json` в текущей директории. В конце работы в консоли также выводится сравнение исходного и нового файлов в стиле `git diff`, чтобы было видно внесенные изменения. Обрабатываются только элементы Bitwarden с `type == 1`; некорректные элементы и URI пропускаются с сообщением в консоли.

## Безопасность

Для изменения URI или удаления истории паролей нужен **незашифрованный JSON-экспорт** хранилища. Такой файл содержит чувствительные данные.

После проверки результата импортируйте новый JSON в Bitwarden. Не передавайте эти файлы третьим лицам.

---

<h1 align="center">
  <a id="eng" href="#eng"><b>ENG</b></a>
</h1>

## Why?

Bitwarden may contain outdated links, such as expired password-recovery URLs. Clicking one of them can take you to an obsolete page, forcing you to return to the website, find the login form, and enter your credentials again.

This script keeps vault links clean and predictable: it can reduce URLs to the registrable domain or preserve the subdomain, remove old password history, and process the entire export at once. This is useful before importing the cleaned vault back into Bitwarden, especially when the vault contains many entries.

## Features

- ### URI converter

  Convert web URIs either to the registrable domain or to the full subdomain/domain/public-suffix host. The modes are mutually exclusive. URIs without a scheme and `http`/`https` URIs are supported; other schemes are skipped.

  **Domain mode:**

  ```bash
  python bwc.py bitwarden_export.json --domain
  ```

  ![](https://github.com/graythze/BitwardenItemCleaner/blob/main/src/pic/domain.jpg)

  **Subdomain mode:**

  ```bash
  python bwc.py bitwarden_export.json --subdomain
  ```

  ![](https://github.com/graythze/BitwardenItemCleaner/blob/main/src/pic/subdomain.jpg)

- ### Password history cleaner

  Use `--rmusedpws` to clear the `passwordHistory` value from login items:

  ```bash
  python bwc.py bitwarden_export.json --rmusedpws
  ```

  ![](https://github.com/graythze/BitwardenItemCleaner/blob/main/src/pic/removeusedpw.jpg)

- ### Combined operation

  URI conversion and password-history cleanup can be used together:

  ```bash
  python bwc.py bitwarden_export.json --domain --rmusedpws
  python bwc.py bitwarden_export.json --subdomain --rmusedpws
  ```

- ### Additional options

  - `--bypassip` (`-byp`) leaves IPv4 and IPv6 URIs unchanged.
  - `--getpsl` (`-psl`) allows `tldextract` to download the Public Suffix List. Without it, the script stays offline.

## Installation

Python 3 and the `tldextract` dependency are required:

```bash
python -m pip install -r requirements.txt
```

## Usage

Pass the path to a Bitwarden JSON export as the first argument:

```bash
python bwc.py <path-to-bitwarden-export.json> [options]
```

Available options:

| Option | Description |
| --- | --- |
| `--domain`, `-dom` | Convert web URIs to the registrable domain only. |
| `--subdomain`, `-subd` | Keep the subdomain, domain, and public suffix. |
| `--bypassip`, `-byp` | Leave IPv4 and IPv6 URIs unchanged. |
| `--rmusedpws`, `-rmpw` | Remove the `passwordHistory` field value from login items. |
| `--getpsl`, `-psl` | Download the Public Suffix List from the network. |

The URI conversion modes are mutually exclusive. Web URIs without a scheme and URIs using `http` or `https` are processed; other schemes are skipped. Without `--domain` or `--subdomain`, URIs are left unchanged, while `--rmusedpws` can still be used on its own.

Examples:

```bash
python bwc.py vault.json --domain
python bwc.py vault.json --subdomain --bypassip
python bwc.py vault.json --rmusedpws
python bwc.py vault.json --domain --getpsl
```

The script creates an output file named `bw_cleaned<timestamp>.json` in the current directory. At the end, the console also shows a `git diff`-style comparison of the original and new files so you can review the changes. Only Bitwarden items with `type == 1` are processed. Invalid items and URI values are skipped with a console message.

## Security

An **unencrypted JSON export** is required to edit URIs or remove password history. It contains sensitive vault data.

After checking the result, import the new JSON file into Bitwarden vault. Do not share these files with third parties.
