:: 批量执行状态码清洗
@echo off
for %%i in (*full.txt) do (
	python36 statusCodeClean.py -f %%i
)
:: python36 subdomain.py -f %%i
:: python 文件名不可是中文
:: do  () ，do后面必须有一个空格。
