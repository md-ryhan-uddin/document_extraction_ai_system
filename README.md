# Document AI System

A comprehensive document processing system that uses a hosted large language model API to extract content from any document (PDF, images, scanned papers), with support for Bangla and English and for structured, semi-structured, and unstructured formats.

**Developed by Md. Ryhan Uddin**

---

## Table of Contents

- [Features](#features)
- [Demo Videos](#demo-videos)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [REST API](#rest-api)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Features in Detail](#features-in-detail)
- [Database Schema](#database-schema)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Recent Fixes](#recent-fixes)
- [Deployment](#deployment)
- [Support](#support)

---

## Features

### Core Capabilities
- **Multi-format Support**: PDF, JPG, PNG, TIFF, BMP
- **Automatic Rotation Detection**: Detects and corrects document orientation (0/90/180/270 degrees)
- **AI-Powered Extraction**: Uses a hosted large language model API with structured JSON schema output (model configured via environment variables)
- **Multi-language Support**: Bangla, English, and mixed content
- **Modern Web Interface**: Drag-and-drop upload, document viewer, search functionality
- **RESTful API**: Full REST API for document upload, processing, and search
- **Admin Interface**: Django admin for data management

### Advanced Content Extraction
- Paragraphs, headings, lists
- Tables with nested columns (unlimited depth)
- Forms with field detection
- Handwriting recognition
- Signatures and images
- Nested Table Normalization: Handles complex tables with sub-columns at any depth

### UI Features
- Responsive card-based document display
- Real-time processing progress with percentage
- Sticky header with scroll animations
- Scroll-to-top button
- Document search, filter, and sort
- Download blocks in multiple formats (TXT, CSV, XLSX, PDF)
- Time and date display for uploads
- Status badges with processing animations

---

## Demo Videos

<table>
<tr>
<td width="50%">

### 📤 Document Upload Process
![Upload Demo](./demo/upload.gif)

</td>
<td width="50%">

### ✅ Content Extraction Results
![Extraction Demo](./demo/extracted.gif)

</td>
</tr>
</table>

> 🎥 **[Watch Full Demo Video](./demo/full_demo_video.mp4)** - Complete end-to-end system demonstration

---

## Tech Stack

- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: Django Templates + Bootstrap 5 + jQuery + Font Awesome
- **AI**: Hosted large language model (configured via environment variables) with structured JSON output  
- **Document Processing**: PyMuPDF (fitz), Pillow, OpenCV
- **Image Processing**: Pillow, OpenCV for rotation detection
- **Export Libraries**: openpyxl (Excel), reportlab (PDF), python-docx (Word)

---

## Quick Start

### Prerequisites Check

Before starting, ensure you have:
- ✓ Hosted LLM API key (add to `.env` per `.env.example`; model selection is configured via environment variables)
- ✓ pip package manager

### 5-Minute Setup

```bash
# 1. Navigate to project directory
cd document_ai_system

# 2. Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your AI API key

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser (optional)
python manage.py createsuperuser

# 7. Start server
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

### First Steps

1. **Home Page** - Upload your first document
   - Go to http://127.0.0.1:8000/
   - Drag and drop a PDF or image file
   - Wait for processing (you'll see status updates with percentage)

2. **View Extracted Content**
   - Click "View" on a completed document
   - Browse pages and extracted content
   - See tables, forms, and structured data
   - Download sections in various formats

3. **All Documents Page**
   - Click "All Documents" in navigation
   - Search by title
   - Filter by status
   - Sort by date, title, or size

4. **Admin Panel** - Explore the data
   - Go to http://127.0.0.1:8000/admin/
   - Login with your superuser credentials
   - Browse documents, pages, content blocks, etc.

---

## Installation

### Step 1: Clone the Repository

```bash
cd document_ai_system
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Django 5.x
- Django REST Framework
- OpenAI Python SDK
- PyMuPDF (for PDF processing)
- Pillow (for image processing)
- OpenCV (for rotation detection)
- openpyxl (for Excel export)
- reportlab (for PDF export)
- python-docx (for Word export)
- And other required packages

### Step 4: Configure Environment Variables

1. Copy the example environment file:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

2. Edit `.env` and add your API key:
```
API_KEY=sk-your-actual-api-key-here
```

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Optional but Recommended)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 7: Run the Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

---

## Usage

### Web Interface

#### 1. Home Page (`http://127.0.0.1:8000/`)
- Drag and drop documents to upload
- View 6 latest documents with status
- Real-time processing progress with percentage
- Click "View All Documents" to see full list
- Action buttons: View, Retry (for failed), Delete

#### 2. All Documents Page (`http://127.0.0.1:8000/all-documents/`)
- View all uploaded documents
- Search by title
- Filter by status (all, completed, processing, failed, cancelled)
- Sort by newest, oldest, title, or size
- Same card design as home page

#### 3. Document Viewer (`http://127.0.0.1:8000/viewer/<id>/`)
- View document pages
- Browse extracted content blocks
- View tables, forms, and structured data
- Search within document
- Download sections in multiple formats:
  - TXT (ASCII table format)
  - CSV (comma-separated values)
  - XLSX (Excel with styled headers)
  - PDF (professional table formatting)
  - JSON (raw data)

#### 4. Admin Interface (`http://127.0.0.1:8000/admin/`)
- Manage documents, pages, and content
- View extraction logs
- Advanced filtering and search

### UI Features

#### Processing Progress Bar
- Shows percentage based on elapsed time vs estimated completion
- Estimation: 7 seconds per page
- Displays 0-95% during processing
- Reaches 100% only on completion
- Positioned below page info and above action buttons

#### Sticky Header
- Fixed navigation that shrinks on scroll
- Smooth transitions and animations
- Navigation links: Home, All Documents
- Developer credit in footer

#### Scroll-to-Top Button
- Appears after scrolling 300px down
- Circular button with gradient background
- Smooth scroll animation
- Hover effect with upward lift

#### Document Cards
- Display time and date of upload
- Show file size and page count
- Status badges with gradients
- Processing animations
- Responsive design

---

## REST API

### Upload Document
```bash
POST /api/documents/
Content-Type: multipart/form-data

{
  "title": "My Document",
  "file": <file>
}
```

### List Documents
```bash
GET /api/documents/
```

### Get Document Details
```bash
GET /api/documents/{id}/
```

### Get Pages for Document
```bash
GET /api/documents/{id}/pages/?include_content=true
```

### Search Content
```bash
GET /api/documents/search/?q=search_term&document_id=1&block_type=table
```

### Get Page Content
```bash
GET /api/pages/{id}/
```

### Reprocess Document
```bash
POST /api/documents/{id}/reprocess/
```

### Download Original Document
```bash
GET /api/documents/{id}/download-original/
```

### Download Tables Only
```bash
GET /api/documents/{id}/download-tables/?format=xlsx
```

### Download Content Block
```bash
GET /api/blocks/{id}/export/?export_format=pdf
```

### API Documentation

Full API documentation is available at: `http://127.0.0.1:8000/api/`

### Test the API

#### Upload a Test Document
```bash
curl -X POST http://127.0.0.1:8000/api/documents/ \
  -F "title=Test Document" \
  -F "file=@/path/to/your/document.pdf"
```

#### Get All Documents
```bash
curl http://127.0.0.1:8000/api/documents/
```

#### Search Content
```bash
curl "http://127.0.0.1:8000/api/documents/search/?q=your_search_term"
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Your API key | Required |
| `MODEL_NAME` | AI model to use | `gpt-4o` |
| `DEFAULT_DPI` | Default DPI for rendering | `150` |
| `HIGH_DPI` | DPI for retry on low confidence | `300` |
| `LOW_CONFIDENCE_THRESHOLD` | Confidence threshold for retry | `0.7` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `52428800` (50MB) |

### Processing Rules

1. **Rotation Detection**: Automatically detects best orientation before extraction
2. **Language Detection**: Auto-detected (en/bn/bn+en)
3. **Nested Tables**: Handles any depth automatically using column_path notation
4. **Confidence Retry**: Automatically retries at higher DPI if confidence is low
5. **Default Structure**: Every block has `table_data` and `form_data` fields (empty if not applicable)

---

## Project Structure

```
document_ai_system/
├── docai_project/          # Django project settings
│   ├── settings.py
│   └── urls.py
├── documents/              # Main app
│   ├── models.py          # Database models
│   ├── views.py           # API views and template views
│   ├── serializers.py     # DRF serializers
│   ├── admin.py           # Admin interface
│   ├── urls.py            # URL routing
│   ├── services/          # Core services
│   │   ├── rotation_detector.py
│   │   ├── ai_extractor.py
│   │   └── document_processor.py
│   └── templates/         # HTML templates
│       └── documents/
│           ├── base.html
│           ├── home.html
│           ├── all_documents.html
│           └── viewer.html
├── media/                 # Uploaded files
│   ├── documents/         # Original files
│   └── pages/             # Extracted page images
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore
├── manage.py
└── README.md
```

---

## Features in Detail

### System Architecture

```
Document Upload
    ↓
File Type Detection (PDF/Image)
    ↓
Page Extraction & Rendering (150-300 DPI)
    ↓
Rotation Detection (0/90/180/270)
    ↓
AI model Extraction (JSON Schema)
    ↓
Database Storage (Relational)
    ↓
REST API + UI Access
```

### Rotation Detection

The system uses OpenCV to automatically detect document orientation:
- Analyzes edge density and line orientation
- Calculates horizontal/vertical variance ratios
- Detects horizontal text lines using Hough transform
- Selects best rotation from 0/90/180/270 degrees

### AI Integration

Uses model with structured output (JSON schema):
- Strictly typed response format
- Guaranteed structure for all content types
- Supports complex nested tables
- Handles multiple languages
- Returns confidence scores

### Nested Table Normalization

Example of nested columns:
```
| Company (Level 0) |  Financials (Level 0)       |
|                   |  Revenue (Level 1) | Costs  |
|                   |  Q1    | Q2        |        |
```

Represented as:
- Company: `column_path=[0]`
- Financials: `column_path=[1]`
- Revenue: `column_path=[1,0]`
- Q1: `column_path=[1,0,0]`
- Q2: `column_path=[1,0,1]`
- Costs: `column_path=[1,1]`

### Download Formats

#### TXT Format
- ASCII table with borders and columns
- Text alignment for readability
- Preserves table structure

#### CSV Format
- Standard comma-separated values
- Headers row
- Proper escaping and quoting

#### XLSX Format
- Styled Excel spreadsheet
- Blue headers with white text
- Borders and auto-column width
- Professional appearance

#### PDF Format
- Professional table formatting
- Alternating row colors
- Custom styling
- Proper pagination

---

## Database Schema

### Core Models

1. **Document**: Uploaded files and metadata
   - title, file, file_size, total_pages
   - status (uploaded, processing, completed, failed, cancelled)
   - uploaded_at, processed_at

2. **Page**: Individual pages with rotation and language info
   - page_number, image, rotation_applied
   - language, page_type, confidence
   - processed_at

3. **ContentBlock**: Extracted content blocks
   - block_type (paragraph, heading, table, form, etc.)
   - text_content, order, confidence
   - table_data, form_data

4. **TableCell**: Individual table cells with nested column support
   - row_number, column_path
   - text, rowspan, colspan

5. **FormField**: Form fields with values
   - field_name, field_label, field_type
   - field_value, is_filled

6. **ExtractionLog**: Logs of all API calls for debugging
   - model_used, tokens_used
   - response_time, error_message

### Nested Table Structure

Tables support unlimited nesting using `column_path`:
- `[0]` - First top-level column
- `[0, 1]` - Second sub-column under first column
- `[0, 1, 2]` - Third sub-sub-column

---

## Development

### Running Tests

```bash
python manage.py test
```

### Database Migrations

After modifying models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Switching to PostgreSQL

1. Install PostgreSQL and psycopg2:
```bash
pip install psycopg2-binary
```

2. Update `.env`:
```
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=docai_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

3. Update `settings.py` to use these environment variables

### What Gets Extracted?

The system extracts:

#### 1. Text Content
- Paragraphs
- Headings
- Lists
- Handwritten text

#### 2. Tables
- Headers (including nested columns)
- Rows and cells
- Cell spanning
- Nested column structure

#### 3. Forms
- Field names and labels
- Field types (text, checkbox, radio, etc.)
- Current values
- Fill status

#### 4. Metadata
- Language detection (Bangla/English/Mixed)
- Page type classification
- Rotation information
- Confidence scores

### System Flow

```
1. Upload Document → 2. Detect File Type → 3. Extract Pages
                              ↓
4. Detect Rotation → 5. Apply Correction → 6. Send to AI model
                              ↓
7. Extract Content → 8. Parse JSON → 9. Store in Database
                              ↓
10. Available via API/UI
```

---

## Troubleshooting

### Common Issues

#### 1. AI API Error
**Problem:** API calls failing or schema validation errors

**Solutions:**
- Verify your API key is correct in `.env` file
- Check you have GPT-4o access
- Ensure you have sufficient credits
- Restart the server after configuration changes

#### 2. PDF Processing Error
**Problem:** PDF files not processing correctly

**Solutions:**
- Verify PyMuPDF is installed correctly: `pip install PyMuPDF`
- Check file permissions
- Ensure PDF is not corrupted or password-protected

#### 3. Image Processing Error
**Problem:** Images failing to process

**Solutions:**
- Install OpenCV: `pip install opencv-python`
- Verify Pillow is installed: `pip install Pillow`
- Check image format is supported (JPG, PNG, TIFF, BMP)
- RGBA images are automatically converted to RGB

#### 4. Database Locked Error
**Problem:** SQLite database locked

**Solutions:**
- Close other connections to the database
- Delete db.sqlite3 and run migrations again (development only)
- Consider switching to PostgreSQL for production

#### 5. ModuleNotFoundError
**Problem:** Missing Python packages

**Solution:**
```bash
pip install -r requirements.txt
```

#### 6. Port Already in Use
**Problem:** Port 8000 is already in use

**Solution:**
```bash
python manage.py runserver 8080
```

#### 7. Download Not Working
**Problem:** Downloads returning 404 or format errors

**Solutions:**
- Verify server is restarted after code changes
- Check that openpyxl and reportlab are installed
- Clear browser cache
- Check browser console for errors

### Verification After Setup

After setting up, verify:

1. **Server Running**
   - Terminal shows "Starting development server"
   - No error messages

2. **Upload Works**
   - Drag and drop a document
   - Status changes to "processing"

3. **Processing Succeeds**
   - Terminal shows "Extraction completed in X.XXs"
   - Status changes to "completed"
   - Progress bar reaches 100%

4. **Content Extracted**
   - Click "View" on completed document
   - See extracted text, tables, forms

5. **Downloads Work**
   - Click download buttons in viewer
   - Files download in correct format

---

## Recent Fixes

### Critical Bugs Fixed

#### 1. Download URL Mismatch
**Problem:** Frontend calling `/download-original/` but backend creating `/download_original/`

**Fix:** Added `url_path` parameters to @action decorators in views.py
```python
@action(detail=True, methods=['get'], url_path='download-original')
@action(detail=True, methods=['get'], url_path='download-tables')
@action(detail=True, methods=['get'], url_path='export')
```

#### 2. Table Formatting in Downloads
**Problem:** Tables downloading as plain text instead of structured format

**Fix:** Redesigned all export formats to preserve table structure
- TXT: ASCII table with borders
- CSV: Headers + rows
- XLSX: Styled headers with colors and borders
- PDF: Professional tables with alternating colors

#### 3. AI Schema Validation
**Problem:** Missing required fields in JSON schema

**Fixes:**
- Table cells: Added `rowspan` and `colspan` to required fields
- Form fields: Added `field_label` to required fields

#### 4. RGBA Image Format Error
**Problem:** PNG images with transparency cannot be saved as JPEG

**Fix:** Automatic conversion from RGBA to RGB with white background
```python
if corrected_image.mode == 'RGBA':
    rgb_image = Image.new('RGB', corrected_image.size, (255, 255, 255))
    rgb_image.paste(corrected_image, mask=corrected_image.split()[3])
    corrected_image = rgb_image
```

#### 5. DRF Format Suffix Conflicts
**Problem:** Query parameter `format` conflicting with DRF's format suffix

**Fix:** Changed to `export_format` parameter

### Files Modified

Recent fixes applied to:
1. `documents/views.py` - URL paths and export logic
2. `documents/services/ai_extractor.py` - Schema validation
3. `documents/services/document_processor.py` - RGBA image handling
4. `documents/templates/documents/home.html` - UI improvements
5. `documents/templates/documents/all_documents.html` - New page
6. `documents/templates/documents/base.html` - Sticky header, scroll button
7. `documents/urls.py` - All documents route

---

## Deployment

### Performance Optimization

1. **DPI Settings**: Lower DPI (150) is faster, higher DPI (300) is more accurate
2. **Database**: Use PostgreSQL for better concurrent access
3. **Caching**: Implement Redis for API response caching
4. **Async Processing**: Use Celery for background document processing
5. **API Rate Limits**: Monitor AI API usage and implement rate limiting

### Security Considerations

1. Change `SECRET_KEY` in production
2. Set `DEBUG=False` in production
3. Configure `ALLOWED_HOSTS` properly
4. Use environment variables for sensitive data
5. Implement user authentication for production use
6. Set up HTTPS for production deployment
7. Enable CSRF protection
8. Implement file upload validation

### Basic Production Setup

1. Set environment variables:
```bash
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

2. Install production dependencies:
```bash
pip install gunicorn psycopg2-binary
```

3. Collect static files:
```bash
python manage.py collectstatic
```

4. Use a production server (Gunicorn):
```bash
gunicorn docai_project.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

5. Set up Nginx as reverse proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

6. Use systemd or supervisor for process management
7. Set up SSL with Let's Encrypt

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL database
- [ ] Set up Gunicorn
- [ ] Configure Nginx reverse proxy
- [ ] Collect static files
- [ ] Set up SSL/HTTPS
- [ ] Implement user authentication
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up Celery for async processing
- [ ] Implement rate limiting
- [ ] Configure CORS if needed

---

## Future Enhancements

Potential improvements:
- User authentication and multi-tenancy
- Document versioning
- Advanced search with Elasticsearch
- Batch processing queue
- Webhook notifications
- Mobile app
- Real-time collaboration
- OCR fallback for low-quality scans
- Custom extraction templates
- API rate limiting and quotas
- Document comparison
- Audit logging

---

## Support

### Documentation Resources

- Django documentation: https://docs.djangoproject.com/
- DRF documentation: https://www.django-rest-framework.org/
- Bootstrap 5: https://getbootstrap.com/docs/5.0/
- Font Awesome: https://fontawesome.com/

### Getting Help

If you encounter issues:
1. Check the console/terminal for error messages
2. Review the `.env` configuration
3. Verify all dependencies are installed
4. Check the Django logs for details
5. View extraction logs in admin: http://127.0.0.1:8000/admin/documents/extractionlog/

### Expected Behavior

#### Successful Processing
```
Terminal Output:
[timestamp] Extraction completed in 12.34s
[timestamp] Tokens used: 1234
[timestamp] Document processed successfully in 15.67s
```

#### Document Status Flow
1. **Upload** → Status: "uploaded"
2. **Processing starts** → Status: "processing"
3. **Pages extracted** → Each page saved as JPEG
4. **Rotation detected** → Automatic correction applied
5. **AI extraction** → Content extracted
6. **Content stored** → Blocks, tables, forms saved
7. **Completed** → Status: "completed"

---

## Acknowledgments

- **Developer**: Md. Ryhan Uddin
- **Technologies**:
  - Django and Django REST Framework communities
  - PyMuPDF, Pillow, and OpenCV projects
  - Bootstrap and Font Awesome for UI components

---

## License

This is a demo project for educational purposes.

---

**Status:** ✓ All features implemented and tested
**Version:** 1.0.0
**Last Updated:** 2025-11-02

Happy document processing!
