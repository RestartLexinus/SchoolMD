@echo off
chcp 65001 >nul
title Автоматический сброс DNS

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ОШИБКА] Запустите скрипт от имени администратора!
    pause
    exit /b
)

echo Поиск активных сетевых интерфейсов и сброс DNS на автоматический режим...
echo.

:: Перебор всех интерфейсов и установка DHCP для DNS
for /f "tokens=1,2,3*" %%i in ('netsh interface show interface') do (
    if "%%i"=="Включено" (
        echo Настройка интерфейса: %%l
        netsh interface ipv4 set dnsservers name="%%l" source=dhcp >nul 2>&1
    )
    if "%%i"=="Enabled" (
        echo Настройка интерфейса: %%l
        netsh interface ipv4 set dnsservers name="%%l" source=dhcp >nul 2>&1
    )
)

:: Очистка кэша DNS
echo.
echo Очистка кэша DNS...
ipconfig /flushdns >nul

echo.
echo Готово. DNS переключен в автоматический режим.
pause