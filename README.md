# Aguadiamante Dashboard
This repository contains the code for the Agua Diamante Dashboard, a data visualization and management tool built using Streamlit.

## Overview
The Agua Diamante Dashboard is designed to help manage information related to clients, products, and sales for the Agua Diamante company. It allows users to input new data and view existing records in an interactive and user-friendly web interface.

## Features
- Data Input: Add information about clients, products, and sales.
- Data Visualization: View and analyze sales and product data with dynamic charts and tables.
- User-Friendly Interface: Navigate through different sections via a sidebar menu for easy access to various functionalities.

## Pages
The dashboard includes the following main pages:

- Home: Provides an overview and welcome message for users.
- Clients: Add, update, and view client information.
- Products: Manage product data, including new entries and edits.
- Sales: Input and analyze sales data, with options to visualize trends and performance over time.
- Reports: Generate custom reports based on the selected parameters and data.

## Tech Stack
- Frontend: Streamlit for building interactive web applications.
- Backend: Python for server-side logic.
- Database: CockroachDB, a distributed SQL database that operates similarly to PostgreSQL.
- Database Library: Uses psycopg2 to connect and interact with the CockroachDB database.

## Getting Started
### Prerequisites
- Python 3.x
- Streamlit

### Installation
1. Clone the repository:
```bash
git clone https://github.com/grudloff/aguadiamante_dashboard.git
cd aguadiamante_dashboard
```
2. Install required packages:

```bash
pip install -r requirements.txt
```
3. Configure the database connection:

Set up your CockroachDB credentials and connection string in the .env file:

```makefile
COCKROACHDB_URI=your_connection_string
```

4. Run the application:

```bash
streamlit run Diamante_Agua_Pura.py
```

### Usage
Once the app is running, open the provided local URL in your browser to access the dashboard. Use the sidebar to navigate between different sections for inputting and viewing data.
