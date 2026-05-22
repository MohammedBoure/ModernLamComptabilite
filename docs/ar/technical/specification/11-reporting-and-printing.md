# 11 - Reporting, Impression et Export

توثق هذه الوثيقة متطلبات الطباعة والتصدير.

## التقارير المطلوبة

| التقرير | الفترة | المصدر | المخرج |
| --- | --- | --- | --- |
| Depenses Caisse | شهري | cash_expenses | PDF/Excel |
| Differences | شهري | cash_closures | PDF/Excel |
| Mouvement Caisse | شهري | cash_movements | PDF/Excel |
| Mouvement Coffre | شهري | coffer_movements | PDF/Excel |
| Bilan Mensuel | شهري | monthly_balances | PDF |
| Journal Fournisseurs | شهري | supplier_transactions | PDF/Excel |
| Etat Fournisseurs | شهري/سنوي | suppliers/payments | PDF/Excel |
| Etat Sous-Traitants | شهري/سنوي | subcontractors/conventions | PDF/Excel |
| Presence | شهري | employee_attendance | PDF/Excel |
| Rapport de Salaire | شهري | salary_reports | PDF/Excel |
| Vehicule Service | شهري | vehicle_expenses | PDF/Excel |
| Etat Cheques | سنوي | cheques | PDF/Excel |
| Etat d'Encaissement | شهري | encashments | PDF رسمي |
| Employes | حسب الحاجة | employees | PDF/Excel |
| Contrats | حسب الحاجة | employee_contracts | PDF/Excel |
| Conges | سنوي | leave_balances | PDF/Excel |

## شكل PDF الرسمي

كل PDF رسمي يحتوي:

- شعار ModernLam.
- اسم المخبر.
- العنوان والهاتف والبريد إن توفر.
- عنوان التقرير.
- الفترة.
- تاريخ الطباعة.
- اسم المستخدم الذي طبع.
- جدول منسق.
- مجموع نهائي.
- مكان cachet/signature عند الحاجة.

## Draft vs Officiel

يعتمد التصميم حالتين للتقارير:

- `Draft`: للتجربة والمراجعة، يظهر عليه وسم Draft.
- `Officiel`: نسخة رسمية تحفظ في سجل الطباعة.

## Export Excel

Excel يجب أن يكون مفيدا للمراجعة، وليس مجرد صورة:

- كل عمود في خلية مستقلة.
- الأرقام كأرقام قابلة للجمع.
- التواريخ كتواريخ.
- صفوف total واضحة.
- Sheet منفصل عند الحاجة لكل قسم.

## أسماء الملفات

صيغة مقترحة:

```text
modernlam-{rapport}-{annee}-{mois}.{extension}
```

أمثلة:

- `modernlam-bilan-mensuel-2026-02.pdf`
- `modernlam-presence-2026-02.xlsx`
- `modernlam-etat-cheques-2026.pdf`

## سجل الطباعة

كل export رسمي يسجل:

- report_name
- period
- format
- generated_by
- generated_at
- file_path

## متطلبات Etat d'Encaissement

يعد هذا التقرير خاصا بالتصريح الضريبي، لذلك يتطلب ضبطا رسميا:

- A4 Portrait.
- Header واضح.
- جدول أيام الشهر.
- Total.
- Cachet et signature.
- لا يطبع كصفحة مكسورة أو ناقصة.

## معاينة قبل الطباعة

قبل توليد PDF رسمي:

1. يعرض النظام preview.
2. يتم تحديد نوع النسخة: Draft أو Officiel.
3. إذا كان Officiel، يسجل النظام العملية.
4. يمكن إعادة طباعة نفس النسخة لاحقا.
