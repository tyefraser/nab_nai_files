# **NAB NAI Files Processor**  
A robust Python-based solution for processing NAB NAI (National Australia Bank's Narrative Account Information) files.

---

## **📌 Overview**
This project provides a **Python-based solution** for processing **NAI files**, enabling efficient data **cleaning, validation, and structuring** for further analysis.

---

## **📂 Project Structure**
```
nab_nai_files-main/
│── .gitignore                  # Excludes unnecessary files from Git tracking
│── README.md                   # Project documentation
│── config.yaml                  # Configuration settings for the parser
│── requirements.txt             # Required dependencies for automated installation
│── requirements_manual.txt      # Manual installation dependencies
│── documentation/               # NAB documentation & reference working files
│── folder_input/                # Placeholder directory for input NAI files
│── src/                         # Source code directory
│   │── checks.py                # Implements validation checks for NAI data
│   │── logger.py                # Configures logging for debugging & error handling
│   │── main.py                  # Main entry point for processing NAI files
│   │── outputs.py               # Handles output generation (CSV, JSON, logs)
│   │── parse_nai_file.py        # Core script for parsing NAI files
│   │── utils.py                 # Utility functions used across the project
```

---

## **⚡ Features**
✅ **Reads & Cleans NAI Files**: Removes unwanted characters, merges continuation lines, and normalizes data.  
✅ **Validates Data**: Runs a series of checks to ensure data consistency.  
✅ **Generates Structured Outputs**: Converts NAI files into structured **CSV, JSON, and logs**.  
✅ **Supports Configurable Processing**: Uses `config.yaml` for easy configuration.  
✅ **Logs Processing Details**: Implements detailed logging for debugging and monitoring.  

---

## **🔧 Installation Guide**

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-repo/nab_nai_files-main.git
cd nab_nai_files-main
```

### **2️⃣ Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## **🚀 Usage**
### **Run the Main Script**
```bash
python src/main.py
```
The script will process all `.nai` files in the `folder_input/` directory.

### **Output Selection**
You can specify which outputs to generate by providing arguments. Available output options:
- `checks`
- `raw_content`
- `cleaned_content`
- `nai_dict`
- `df_file_metadata`
- `df_groups`
- `df_accounts`
- `df_transactions`
- `df_accounts_structured`
- `df_transactions_structured`

#### **Example Usage**
Run **all outputs**:
```bash
python src/main.py checks,raw_content,cleaned_content,nai_dict,df_file_metadata,df_groups,df_accounts,df_transactions,df_accounts_structured,df_transactions_structured
```
Run only `checks` and `raw_content`:
```bash
python src/main.py checks,raw_content
```

---

## **⚙️ Configurable Parameters**
The `config.yaml` file contains key configurations such as input and output folders.

Example:
```yaml
input_folder_path: "folder_input"
output_folder_path: "folder_output"
```

---

## **📝 Example Workflow**
1️⃣ **Place `.nai` files** in the `folder_input/` directory.  
2️⃣ **Run the script**:
   ```bash
   python src/main.py
   ```
3️⃣ **Check the output** in `folder_output/`:
   - ✅ CSV files  
   - ✅ JSON reports  
   - ✅ Logs  

---

## **🛠 Development & Contribution**
### **1️⃣ Code Formatting & Standards**
This project follows **PEP 8** coding standards. Use `flake8` for linting:
```bash
pip install flake8
flake8 src/
```

### **2️⃣ Running Tests**
If unit tests are implemented, they can be run using:
```bash
pytest tests/
```

### **3️⃣ Contributing**
- Fork the repository.  
- Create a new branch (`feature-new-functionality`).  
- Commit changes and open a **Pull Request**.  

---

## **📧 Contact**
For issues or inquiries, please reach out via **GitHub Issues**.

---

### **🚀 Happy Coding & File Processing! 🎯**
