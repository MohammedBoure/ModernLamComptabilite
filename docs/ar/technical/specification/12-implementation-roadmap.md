# 12 - Plan d'Implementation

توثق هذه الوثيقة خطة تنفيذ عملية لتحويل المواصفات إلى برنامج.

## المرحلة 0 - تثبيت القرارات

قبل البرمجة:

- اختيار نوع التطبيق: Web محلي، Desktop، أو شبكة داخلية.
- اختيار قاعدة البيانات.
- تثبيت قاعدة Chiffre d'affaires LAM.
- تثبيت قواعد salaire وconge.
- تحديد صلاحيات المستخدمين.
- تحديد هل SOFTLAM import أم إدخال يدوي.

## المرحلة 1 - أساس المشروع

المخرجات:

- إعداد المشروع.
- إعداد قاعدة البيانات.
- نظام تسجيل الدخول.
- roles/permissions.
- accounting periods.
- audit logs.

الشاشات:

- Login
- Dashboard بسيط
- Administration users
- Periods management

## المرحلة 2 - Caisse & Coffre

المخرجات:

- Depenses caisse.
- Differences.
- Mouvement caisse.
- Entrees supplementaires.
- Sorties coffre.
- Calcul Coffre Net Reel.

الشاشات:

- Cloture Caisse
- Caisse & Coffre
- Resume Coffre

## المرحلة 3 - Fournisseurs وSous-Traitants

المخرجات:

- Fournisseurs.
- Journal des depenses.
- Payments.
- Sous-traitants.
- Conventions.
- Etats correspondants.

الشاشات:

- Fournisseurs
- Details fournisseur
- Sous-Traitants
- Conventions
- Etat Fournisseurs
- Etat Sous-Traitants

## المرحلة 4 - Bilan et Profitabilite

المخرجات:

- Bilan Mensuel.
- Profitabilite reelle.
- Mouvement Profitabilite.
- ترحيل الربحية.
- غلق الشهر.

الشاشات:

- Bilan Mensuel
- Profitabilite
- Cloture Mois

## المرحلة 5 - Presence et Salaires

المخرجات:

- Presence monthly grid.
- حساب مجاميع الحضور.
- Rapport de salaire.
- اعتماد الرواتب.

الشاشات:

- Presence
- Rapport de Salaire
- Salary details

## المرحلة 6 - DRH

المخرجات:

- Employes.
- Contrats.
- Conges.
- Documents.
- Alerts.

الشاشات:

- Liste Employes
- Fiche Employe
- Contrats
- Conges

## المرحلة 7 - Etats وPrinting

المخرجات:

- Etat d'Encaissement.
- Etat Cheques.
- Vehicule service.
- Export PDF/Excel.
- سجل الطباعة.

الشاشات:

- Etats
- Preview impression
- Historique exports

## المرحلة 8 - مراجعة نهائية

المخرجات:

- اختبارات الحسابات.
- مراجعة الصلاحيات.
- مراجعة الطباعة.
- Backup.
- دليل استعمال مختصر.

## أول MVP مقترح

للحصول على نسخة مفيدة بسرعة:

1. Login + periods.
2. Cloture Caisse.
3. Mouvement Caisse/Coffre.
4. Fournisseurs.
5. Bilan Mensuel.
6. Etat d'Encaissement PDF.

بعد ذلك تضاف DRH والرواتب.

## معايير قبول عامة

- كل شاشة تحفظ وتقرأ من قاعدة البيانات.
- كل مبلغ ظاهر يمكن معرفة مصدره.
- لا تظهر أخطاء تقنية للمستخدم مثل `#DIV/0!`.
- كل تقرير رسمي يطبع بنفس الفترة المختارة.
- لا يوجد تعديل في شهر مغلق بدون audit log.
