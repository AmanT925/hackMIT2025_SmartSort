# SmartSort - Intelligent File Organization System

SmartSort is an intelligent file organization system that automatically categorizes and organizes your files using advanced analysis and machine learning. It helps you keep your digital files neatly organized without manual effort.

## 🚀 Features

- **Automatic File Categorization**: Automatically sorts files into appropriate categories based on content and file type
- **Multi-format Support**: Handles various file types including documents, images, PDFs, spreadsheets, and more
- **Smart Naming**: Suggests better filenames based on file content
- **Duplicate Detection**: Identifies and helps manage duplicate files
- **Web Interface**: Easy-to-use web interface for managing and organizing files
- **RESTful API**: Built with FastAPI for easy integration with other services

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React.js, TypeScript
- **File Processing**: PyPDF2, python-pptx, openpyxl, Pillow, pytesseract
- **Database**: SQLite (for metadata storage)
- **AI/ML**: Content analysis for intelligent categorization

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Tesseract OCR (for text extraction from images)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hackMIT2025_SmartSort.git
   cd hackMIT2025_SmartSort
   ```

2. **Set up the backend**
   ```bash
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Start the frontend development server** (in a new terminal)
   ```bash
   cd frontend
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## 📁 Project Structure

```
hackMIT2025_SmartSort/
├── backend/              # Backend Python code
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── file_analyzer.py # File analysis logic
│   └── database_manager.py # Database operations
├── frontend/            # Frontend React application
├── uploads/             # Default upload directory
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 📄 Supported File Types

- **Documents**: PDF, DOCX, TXT, PPTX
- **Spreadsheets**: XLSX, CSV
- **Images**: JPG, PNG, GIF (with text extraction)
- **Code**: Python, JavaScript, and more

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
