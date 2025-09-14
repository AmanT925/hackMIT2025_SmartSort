import os
import random
from datetime import datetime, timedelta

# Sample content for different file types
document_content = {
    "resume": "John Doe\nSenior Software Engineer\n\nSkills: Python, JavaScript, React, Node.js, AWS\nExperience: 5+ years in full-stack development\nEducation: B.S. in Computer Science - MIT 2018",
    "cover_letter": "Dear Hiring Manager,\n\nI am excited to apply for the position at your company.\n\nSincerely,\nJohn Doe",
    "contract": "AGREEMENT\n\nThis Agreement is made on {date} between Company and Client.\n\n1. Services to be provided...",
    "invoice": "INVOICE #{num}\nDate: {date}\n\nDescription\t\tAmount\nService 1\t\t$100.00\n\nTotal: $100.00",
    "report": "Quarterly Report {q} {year}\n\nExecutive Summary:\n- Revenue: ${rev}M\n- Expenses: ${exp}M\n- Profit: ${prof}M"
}

# Create sample documents
def create_documents():
    # Resumes
    for i in range(1, 4):
        with open(f'uploads/Documents/Resumes/resume_{i}.pdf', 'w') as f:
            f.write(document_content["resume"])
    
    # Cover Letters
    for i in range(1, 3):
        with open(f'uploads/Documents/Cover_Letters/cover_letter_{i}.docx', 'w') as f:
            f.write(document_content["cover_letter"])
    
    # Contracts
    for i in range(1, 4):
        with open(f'uploads/Documents/Contracts/contract_{i}.pdf', 'w') as f:
            f.write(document_content["contract"].format(date=(datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")))
    
    # Invoices
    for i in range(1, 6):
        with open(f'uploads/Documents/Invoices/invoice_{i:03d}.pdf', 'w') as f:
            f.write(document_content["invoice"].format(num=1000+i, date=(datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")))
    
    # Quarterly Reports
    for year in [2023, 2024]:
        for q in range(1, 5):
            with open(f'uploads/Work/Reports/Q{q}_{year}_Report.pdf', 'w') as f:
                rev = random.randint(50, 200)
                exp = random.randint(20, 150)
                f.write(document_content["report"].format(
                    q=f"Q{q}",
                    year=year,
                    rev=rev,
                    exp=exp,
                    prof=rev-exp
                ))

# Create sample code files
def create_code_files():
    # Python files
    py_code = """def calculate_sum(numbers):
    return sum(numbers)

def main():
    nums = [1, 2, 3, 4, 5]
    print(f"Sum: {calculate_sum(nums)}")

if __name__ == "__main__":
    main()"""
    
    # JavaScript files
    js_code = """const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('Hello World!');
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});"""
    
    # Create Python files
    for i in range(1, 6):
        with open(f'uploads/Code/Python/script_{i}.py', 'w') as f:
            f.write(py_code)
    
    # Create JavaScript files
    for i in range(1, 4):
        with open(f'uploads/Code/JavaScript/app_{i}.js', 'w') as f:
            f.write(js_code)
    
    # Create HTML/CSS files
    for i in range(1, 4):
        with open(f'uploads/Code/HTML_CSS/index_{i}.html', 'w') as f:
            f.write(f'''<!DOCTYPE html>
<html>
<head>
    <title>Project {i}</title>
    <link rel="stylesheet" href="styles_{i}.css">
</head>
<body>
    <h1>Welcome to Project {i}</h1>
    <p>This is a sample HTML file.</p>
</body>
</html>''')
        
        with open(f'uploads/Code/HTML_CSS/styles_{i}.css', 'w') as f:
            f.write(f'''body {{
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #f0f0f0;
}}

h1 {{
    color: #333;
}}''')

# Create sample media files
def create_media_files():
    # Create empty files to represent media
    for i in range(1, 6):
        # Photos
        with open(f'uploads/Media/Photos/photo_{i}.jpg', 'w') as f:
            f.write("")
        
        # Screenshots
        if i <= 3:
            with open(f'uploads/Media/Screenshots/screenshot_{i}.png', 'w') as f:
                f.write("")
    
    # Create a few more specialized media files
    with open('uploads/Media/Videos/presentation_demo.mp4', 'w') as f:
        f.write("")
    with open('uploads/Media/Images/logo.svg', 'w') as f:
        f.write("")

# Create work-related files
def create_work_files():
    # Meeting notes
    for i in range(1, 6):
        with open(f'uploads/Work/Meeting_Notes/meeting_{i}.md', 'w') as f:
            f.write(f"""# Meeting Notes - {datetime.now().strftime('%Y-%m-%d')}

## Attendees
- John Doe
- Jane Smith
- Alex Johnson

## Agenda
1. Review previous action items
2. Project updates
3. New business
4. Action items""")
    
    # Presentations
    for i in range(1, 4):
        with open(f'uploads/Work/Presentations/presentation_{i}.pptx', 'w') as f:
            f.write("")

# Create personal files
def create_personal_files():
    # Travel
    for i, city in enumerate(['paris', 'tokyo', 'new_york'], 1):
        with open(f'uploads/Personal/Travel/trip_to_{city}.pdf', 'w') as f:
            f.write(f"""Trip to {city.replace('_', ' ').title()}
            
Itinerary:
- Day 1: Arrival and check-in
- Day 2: City tour
- Day 3: Local experiences
- Day 4: Free day
- Day 5: Departure""")
    
    # Health
    with open('uploads/Personal/Health/medical_report_2024.pdf', 'w') as f:
        f.write("Medical Report - Annual Checkup 2024")
    
    # Finance
    for doc in ['tax_return_2023', 'investment_portfolio', 'budget_2024']:
        with open(f'uploads/Personal/Finance/{doc}.xlsx', 'w') as f:
            f.write("")

# Create archive files
def create_archive_files():
    for year in [2022, 2023, 2024]:
        for month in range(1, 13):
            if month <= 3:
                q = 'Q1'
            elif month <= 6:
                q = 'Q2'
            elif month <= 9:
                q = 'Q3'
            else:
                q = 'Q4'
            
            # Skip future months
            if year == 2024 and month > datetime.now().month:
                continue
                
            folder = f'uploads/Archives/{year}/{q}'
            os.makedirs(folder, exist_ok=True)
            
            with open(f'{folder}/backup_{year}_{month:02d}.zip', 'w') as f:
                f.write("")

def main():
    # Create all directories
    os.makedirs('uploads/Documents/Resumes', exist_ok=True)
    os.makedirs('uploads/Documents/Cover_Letters', exist_ok=True)
    os.makedirs('uploads/Documents/Contracts', exist_ok=True)
    os.makedirs('uploads/Documents/Invoices', exist_ok=True)
    os.makedirs('uploads/Media/Images', exist_ok=True)
    os.makedirs('uploads/Media/Screenshots', exist_ok=True)
    os.makedirs('uploads/Media/Photos', exist_ok=True)
    os.makedirs('uploads/Media/Videos', exist_ok=True)
    os.makedirs('uploads/Code/Python', exist_ok=True)
    os.makedirs('uploads/Code/JavaScript', exist_ok=True)
    os.makedirs('uploads/Code/HTML_CSS', exist_ok=True)
    os.makedirs('uploads/Code/Projects', exist_ok=True)
    os.makedirs('uploads/Work/Presentations', exist_ok=True)
    os.makedirs('uploads/Work/Reports', exist_ok=True)
    os.makedirs('uploads/Work/Meeting_Notes', exist_ok=True)
    os.makedirs('uploads/Personal/Travel', exist_ok=True)
    os.makedirs('uploads/Personal/Health', exist_ok=True)
    os.makedirs('uploads/Personal/Finance', exist_ok=True)
    
    # Generate files
    create_documents()
    create_code_files()
    create_media_files()
    create_work_files()
    create_personal_files()
    create_archive_files()
    
    print("Sample files generated successfully!")

if __name__ == "__main__":
    main()
