# main.py
import os
from compliance_checker import check_password_compliance, check_backup_compliance
from ai_reporter import analyze_compliance_data, generate_ai_report
from config import GEMINI_API_KEY

def main():
    """
    تنفيذ النظام الكامل لفحص الامتثال وتوليد التقرير.
    """
    print("=============================================")
    print("     بدء نظام فحص الامتثال والتقارير الآلي     ")
    print("=============================================")
    
    # 1. التحقق من مفتاح الذكاء الاصطناعي
    if "YOUR_GEMINI_API_KEY_HERE" in GEMINI_API_KEY:
         print("\n[تحذير]: يرجى تحديث مفتاح 'GEMINI_API_KEY' في ملف config.py.")

    # 2. تنفيذ فحص الامتثال
    check_password_compliance()
    check_backup_compliance()
    
    # 3. تحليل البيانات
    analysis_results = analyze_compliance_data()
    
    # 4. توليد التقرير بالذكاء الاصطناعي
    if analysis_results:
        report = generate_ai_report(analysis_results)
        
        print("\n\n" + "="*50)
        print("          ✨ التقرير التنفيذي للذكاء الاصطناعي ✨          ")
        print("="*50)
        print(report)
        
        # ******************
        # هنا يمكنك حفظ التقرير في ملف HTML أو رفعه إلى قاعدة البيانات
        # ******************
        
        with open("executive_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("\nتم حفظ التقرير في ملف executive_report.md.")
    else:
        print("\nلا يوجد تقرير لتوليده.")

if __name__ == "__main__":
    main()
