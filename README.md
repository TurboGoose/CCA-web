# CCA-web
![workflow-status](https://github.com/TurboGoose/CCA-web/actions/workflows/cca-web-ci.yaml/badge.svg)


Web version of [Chat-Corpora-Annotator](https://github.com/yakovypg/Chat-Corpora-Annotator).

# Local deployment guide
1. Clone repo
```shell
git clone https://github.com/TurboGoose/CCA-web.git
```

2. `cd` to the root folder of cloned directory
```shell
cd CCA-web
```

3. Create virtual environment (Python 3.9 has to be installed)
```shell
python -m venv venv
```
4. Activate virtual environment

    Linux/MacOS:
    
    ```shell
    . venv/bin/activate
    ```

    Windows:
    ```shell
   venv\Scripts\activate
   ```
5. Install dependencies
```shell
pip install -r requirements.txt
```

6. Init database (if running for the first time)
```shell
python app/main.py init
```

7. Run server
```shell
python app/main.py
```