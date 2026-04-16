# VayalMozhi

VayalMozhi is a comprehensive, bilingual (English/Tamil) agriculture support platform designed to empower farmers and bridge the gap between consumers and sellers. Built with a modern, Neo-Brutalist UI and an accessible architecture, the platform aims to provide farmers with essential digital tools—ranging from an active marketplace to crop disease detection—all in one place.

## Features

- **Bilingual Interface**: Seamless toggling between English and Tamil across all dynamic content, including the marketplace, dashboards, and schemes.
- **Agriculture Marketplace**: 
  - Buy, sell, and rent agricultural assets including machinery, seeds, and livestock.
  - Interactive robust star-rating system for sellers and products.
- **Farmer's Pro Dashboard**:
  - Interactive Profit & Loss Tracker completely integrated with intuitive Neo-Brutalist design.
  - Quick access stats including Total Inquiries, Active Listings, and Saved Schemes.
- **Crop Disease Detection**: Upload crop images to receive immediate insights and both organic and inorganic treatment recommendations.
- **Live Market Prices**: Track the latest market rates for agriculture products, featuring trend indicators (up/down).
- **Government Schemes**: Browse, explore, and save local and national agricultural subsidies right to your profile.

## Technology Stack

- **Backend**: Python 3.7+, Flask, Flask-CORS
- **Frontend**: Vanilla HTML5, CSS3 (Neo-Brutalism Design Concept), JavaScript (ES6)
- **Database**: Lightweight local JSON storage (`/data/*.json`) for easy local persistence.

## Getting Started

Follow these instructions to run the VayalMozhi platform locally on your machine.

### Prerequisites

Ensure you have [Python 3.7+](https://www.python.org/downloads/) installed on your system.

### Install Dependencies

Open your terminal, navigate to the project directory, and install the required Python libraries using pip:

```bash
pip install Flask flask-cors
```

## Project Structure

```
VayalMozhi/
│
├── app.py                   # Main Flask backend application
├── data/                    # JSON "Database" tables
│   ├── prices.json          # Crop market prices data
│   ├── products.json        # Marketplace listings
│   ├── schemes.json         # Government schemes info
│   └── users.json           # User account storage
│
├── static/                  # Static web assets
│   ├── css/
│   │   └── style.css        # Neo-Brutalist styling tokens & rules
│   ├── images/              # Custom brand vectors and product photos
│   └── js/                  # Client-side routing and module logic
│       ├── app.js           # Main routing & application initialization
│       ├── auth.js          # Authentication & Dashboard generation
│       ├── i18n.js          # Dynamic Tamil/English translation
│       ├── marketplace.js   # Products rendering & filtering
│       ├── prices.js        # Crop price rendering and trackers
│       └── schemes.js       # Government schemes & bookmarking
│
├── templates/               
│   └── index.html           # Main Single Page Application structure
│
└── uploads/                 # Directory to store user image uploads
```

## Usage Notes & Data Reset
Since this project uses local JSON files for its database, all changes made locally (creating accounts, uploading products to the marketplace, submitting ratings, processing profit/loss transactions) are persisted. 

If you ever need to reset the platform's data to the default state, simply clear out the dynamically added items in the specific JSON files in the `/data/` folder and delete user-uploaded content inside the `/uploads/` folder.
