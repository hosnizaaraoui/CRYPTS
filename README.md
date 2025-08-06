# CRYPTS

A simple **Terminal User Interface (TUI)** built with [PyTermGUI](https://github.com/bczsalba/pytermgui) to display cryptocurrency market data from [CoinMarketCap](https://coinmarketcap.com/).

![screenshot](screenshot.png)

## ✨ Features

- Fetches **live cryptocurrency prices** from CoinMarketCap  
- Configurable **row limit** for display  
- **Name & price filters** (WIP)  
- **Color-coded** price indicators with up ▲ / down ▼ carets  
- **Screenshot capture** (saves as SVG)  
- **Quit confirmation modal**  

## 🚧 Work in Progress

> This is an early version of the project.  
> The **auto-refresh** (real-time or delay-based) and **filters** are **not fully functional yet**.  
> A big part of the UI logic is done, and the next steps will focus on:
> - Implementing real-time refresh without losing TUI interactivity
> - Making filters apply instantly
> - Adding more statistics columns

## 📦 Installation

```bash
git clone https://github.com/hosnizaaraoui/CRYPTS
cd CRYPTS
pip install -r requirements.txt
