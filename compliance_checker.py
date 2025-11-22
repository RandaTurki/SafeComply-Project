# compliance_checker.py
from db_connector import execute_query
from config import MAX_PASSWORD_AGE_DAYS, MAX_BACKUP_AGE_DAYS
from datetime import datetime, timedelta

def check_password_compliance():
    """
    يفحص امتثال المستخدمين لسياسة عمر كلمة المرور.
    يحدث حقل last_password_change_at إذا لزم الأمر ويحدث سجل الامتثال.
    """
    print("\n--- فحص امتثال كلمة المرور ---")
    
    # حساب التاريخ الأقصى المسموح به لآخر تغيير
    threshold_date = datetime.now() - timedelta(days=MAX_PASSWORD_AGE_DAYS)
    
    # 1. جلب المستخدمين الذين لم يغيروا كلمة المرور منذ فترة طويلة
    # نفترض أن last_password_change_at مسجل في جدول users
    users_to_check = execute_query(
        "SELECT user_id, email, last_password_change_at FROM users WHERE last_password_change_at < %s OR last_password_change_at IS NULL",
        (threshold_date,),
        fetch=True
    )
    
    non_compliant_count = 0
    if users_to_check:
        for user in users_to_check:
            # المنطق: إذا كان المستخدم غير ممتثل (عمره أكثر من 90 يوماً)
            status = 'non_compliant'
            non_compliant_count += 1
            
            # 2. تسجيل حالة عدم الامتثال في جدول compliance_logs
            notes = f"انتهاك سياسة كلمة المرور. لم يتم التغيير منذ {user.get('last_password_change_at', 'التسجيل')}. الحد الأقصى هو {MAX_PASSWORD_AGE_DAYS} يوماً."
            
            execute_query(
                "INSERT INTO compliance_logs (user_id, policy_id, compliance_status, score, notes) VALUES (%s, %s, %s, %s, %s)",
                (user['user_id'], 1, status, 0, notes) # نفترض أن policy_id=1 لسياسة كلمة المرور
            )
            
            print(f"-> [!! غير ممتثل !!] المستخدم: {user['email']}")

    print(f"تم فحص {len(users_to_check)} مستخدم. عدد الحالات غير الممتثلة: {non_compliant_count}")

    # ******************
    # هنا يمكنك إضافة منطق إرسال تنبيه (بريد إلكتروني، رسالة)
    # ******************


def check_backup_compliance():
    """
    يفحص امتثال الأجهزة لسياسة النسخ الاحتياطي ويحدث جدول backup_policies.
    """
    print("\n--- فحص امتثال النسخ الاحتياطي ---")

    threshold_date = datetime.now() - timedelta(days=MAX_BACKUP_AGE_DAYS)

    # 1. جلب سياسات النسخ الاحتياطي التي لم يتم فيها النسخ الاحتياطي منذ فترة طويلة
    backups_to_check = execute_query(
        "SELECT backup_id, device_id, last_backup_at FROM backup_policies WHERE last_backup_at < %s OR last_backup_at IS NULL",
        (threshold_date,),
        fetch=True
    )
    
    non_compliant_count = 0
    if backups_to_check:
        for backup in backups_to_check:
            status = 'non_compliant'
            non_compliant_count += 1

            # 2. تحديث حالة النسخ الاحتياطي في جدول backup_policies
            execute_query(
                "UPDATE backup_policies SET backup_status = %s WHERE backup_id = %s",
                (status, backup['backup_id'])
            )
            
            # 3. تسجيل حالة عدم الامتثال في جدول compliance_logs
            # نحتاج إلى user_id لمعرفة مالك الجهاز، سنقوم بـ JOIN لجلبها
            user_info = execute_query(
                "SELECT user_id FROM devices WHERE device_id = %s",
                (backup['device_id'],),
                fetch=True
            )
            user_id = user_info[0]['user_id'] if user_info else None

            if user_id:
                notes = f"انتهاك سياسة النسخ الاحتياطي. آخر نسخ احتياطي كان بتاريخ {backup.get('last_backup_at', 'N/A')}. الحد الأقصى هو {MAX_BACKUP_AGE_DAYS} يوماً."
                
                execute_query(
                    "INSERT INTO compliance_logs (user_id, policy_id, device_id, compliance_status, score, notes) VALUES (%s, %s, %s, %s, %s, %s)",
                    (user_id, 2, backup['device_id'], status, 0, notes) # نفترض أن policy_id=2 لسياسة النسخ الاحتياطي
                )
                print(f"-> [!! غير ممتثل !!] الجهاز ID: {backup['device_id']}")

    print(f"تم فحص {len(backups_to_check)} سياسة نسخ احتياطي. عدد الحالات غير الممتثلة: {non_compliant_count}")
