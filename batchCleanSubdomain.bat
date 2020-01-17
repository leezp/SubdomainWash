:: 批量执行子域名去重脚本
@echo off
for %%i in (*1_full.txt) do (
	python36 subdomainClean.py -f %%i
)
:: python36 subdomain.py -f %%i
:: python 文件名不可是中文
:: do  () ，do后面必须有一个空格。
