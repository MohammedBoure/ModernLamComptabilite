# 07 - Workflows Fonctionnels

هذا الملف يشرح كيف سيعمل البرنامج عمليا، خطوة بخطوة، من الإدخال اليومي إلى غلق الشهر.

## 07.1 بداية شهر جديد

1. المستخدم يختار الشهر والسنة.
2. إذا لم يكن الشهر موجودا، ينشئ النظام فترة جديدة.
3. ينسخ النظام قوائم الموظفين النشطين وقائمة الموردين كمرجع.
4. تكون حالة الشهر `Ouvert`.
5. يمكن البدء في إدخال caisse, coffre, presence, fournisseurs.

## 07.2 إدخال يومي للصندوق

1. المستخدم يفتح Cloture Caisse.
2. يضيف مصاريف caisse إن وجدت.
3. يدخل Montant Reel.
4. يدخل Montant Virtuelle القادم من SOFTLAM.
5. النظام يحسب Difference.
6. إذا وجدت Difference، يطلب Remarque.
7. بعد الحفظ، تظهر النتيجة في Etat Differences وDashboard.

## 07.3 إدخال حركة caisse الشهرية

1. المستخدم يفتح Caisse & Coffre.
2. يختار اليوم.
3. يدخل Caisse CV, Caisse C, TPE, Depenses, Remboursement, Convention, Sous-Traitants.
4. النظام يحسب Total اليوم.
5. النظام يحدث total/min/max/moyenne للشهر.

## 07.4 إدخال sortie coffre

1. المستخدم يفتح Sorties Coffre.
2. يضيف Date, Designation, Montant, Categorie.
3. يمكن إرفاق وثيقة.
4. بعد الحفظ، ينقص المبلغ من Coffre Net Reel.
5. تظهر العملية في historique.

## 07.5 متابعة fournisseur

1. المستخدم يضيف fournisseur أو يختار الموجود.
2. يضيف facture/commande مع montant.
3. يسجل versement إذا تم الدفع.
4. النظام يحسب reste.
5. إذا تم دفع كامل المبلغ، تتحول الحالة إلى Paye.
6. يظهر المورد في Etat Fournisseurs.

## 07.6 متابعة sous-traitant أو convention

1. المستخدم يضيف عملية جديدة.
2. يدخل Montant.
3. يدخل Versement إن وجد.
4. يختار Mode Paiement.
5. النظام يحسب Reste.
6. تظهر العملية في Etat Sous-Traitants أو Convention.

## 07.7 إدخال الحضور

1. RH يفتح شاشة Presence.
2. يختار الشهر.
3. تظهر قائمة الموظفين النشطين.
4. لكل يوم يدخل الرمز المناسب.
5. النظام يجمع P, ABS, G, GV-J, GV-N, C, C.M, REC, P+.
6. يمكن استعمال هذه النتائج في Rapport de Salaire.

## 07.8 توليد الرواتب

1. RH أو Comptable يفتح Rapport de Salaire.
2. يضغط Generer depuis Presence.
3. النظام يجلب أيام الحضور والغياب والgardes.
4. المستخدم يدخل primes, penalites, avances عند الحاجة.
5. النظام يحسب salaire final حسب القاعدة المعتمدة.
6. التقرير يبقى Brouillon حتى يتم اعتماده.
7. عند الاعتماد يصبح Valide، وعند الدفع يصبح Paye.

## 07.9 إعداد Etat d'Encaissement

1. المستخدم يفتح Etat d'Encaissement.
2. يختار الشهر.
3. النظام يولد أيام الشهر.
4. يملأ designation الافتراضي.
5. المستخدم يراجع montants.
6. يطبع التقرير الرسمي للتصريح.

## 07.10 غلق الشهر

قبل الغلق يجب أن يتحقق النظام من:

- لا توجد فروقات caisse بدون تبرير.
- كل التقارير الأساسية مولدة.
- لا توجد رواتب Brouillon.
- البواقي واضحة للموردين والمتعاملين.
- البيلان الشهري محسوب.

خطوات الغلق:

1. Admin أو Comptable بصلاحية يفتح شاشة Cloture Mois.
2. النظام يعرض checklist.
3. المستخدم يؤكد الغلق.
4. حالة الشهر تصبح `Cloture`.
5. يمنع التعديل العادي.
6. تحفظ لقطة من المجاميع الشهرية.

## 07.11 تعديل شهر مغلق

1. المستخدم يطلب فتح تعديل استثنائي.
2. يجب إدخال سبب.
3. Admin يوافق.
4. النظام يسمح بتعديل محدود.
5. كل تعديل يسجل في audit log.
6. يعاد حساب البيلان.
7. يغلق الشهر مرة أخرى.

## 07.12 ترحيل الربحية

1. عند نهاية الشهر، يحسب النظام profitabilite.
2. إذا بقي جزء مرحل، يسجل في mouvement profitabilite للشهر التالي.
3. عند استعمال الربحية، تسجل عملية mouvement مع detail.
4. يظهر reste profitabilite في Dashboard وبيلان الشهر.
