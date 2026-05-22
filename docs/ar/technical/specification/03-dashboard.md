# 03 - Tableau de Bord

Dashboard هو أول شاشة يراها المستخدم بعد تسجيل الدخول. دوره ليس إدخال البيانات، بل إعطاء صورة سريعة عن الشهر الحالي والتنبيهات المهمة.

## الهدف

- معرفة وضع caisse/coffre بسرعة.
- رؤية chiffre d'affaires والربحية.
- اكتشاف الفروقات والمدفوعات الناقصة.
- الدخول السريع إلى الشاشات التي تحتاج عمل.

## مكونات الشاشة

### شريط الفترة

| الحقل | الوصف |
| --- | --- |
| Mois | الشهر المعروض |
| Annee | السنة |
| Statut du mois | Ouvert, En revision, Cloture |
| Derniere mise a jour | آخر وقت تحديث للحسابات |

### بطاقات الملخص

| البطاقة | المحتوى |
| --- | --- |
| Caisse CV | مجموع Caisse CV للشهر |
| Caisse C | مجموع Caisse C للشهر |
| TPE | مجموع عمليات TPE |
| Depenses | مجموع مصاريف الشهر |
| Coffre Net Reel | صافي الخزنة الحقيقي |
| Chiffre d'Affaires Global | رقم الأعمال الكلي |
| Profitabilite | الربحية قبل الاستثمارات |
| Profitabilite Net | الربحية بعد الاستثمارات |

### التنبيهات

تعرض قائمة مختصرة لأهم ما يحتاج انتباها:

- فروقات caisse غير مبررة.
- fournisseurs لديهم reste.
- conventions أو sous-traitants لم تدفع بالكامل.
- رواتب غير مولدة أو غير مؤكدة.
- موظفون بدون عقد أو تاريخ CNAS.
- شيكات بدون designation أو beneficiary.

### الاختصارات

أزرار دخول سريع:

- Ajouter depense caisse
- Ajouter mouvement coffre
- Saisir presence
- Ajouter paiement fournisseur
- Generer salaires
- Imprimer encaissement

## قواعد الحساب

Dashboard لا يخزن أرقاما يدويا. كل قيمة فيه تحسب من الجداول الأصلية حسب الفترة المختارة.

مصدر البيانات:

- caisse من `cash_movements` و`cash_closures`.
- coffre من `coffer_movements` و`additional_entries`.
- fournisseurs من `supplier_transactions`.
- salaires من `salary_reports`.
- profitabilite من `monthly_balances`.

## حالات العرض

| الحالة | ماذا يظهر |
| --- | --- |
| شهر جديد بدون بيانات | بطاقات بقيم صفرية وروابط بدء الإدخال |
| شهر مفتوح | كل الاختصارات نشطة |
| شهر في المراجعة | الحفظ يحتاج صلاحية comptable أو admin |
| شهر مغلق | قراءة فقط مع إمكانية طباعة التقارير |

## سلوك مهم

- عند وجود فرق caisse، يجب أن يظهر بلون واضح ولا يختفي حتى يضاف تبرير أو تعديل.
- إذا كان `Coffre Net Reel` سالبا، يظهر تنبيه.
- إذا فشل حساب الربحية بسبب قسمة على صفر، لا تعرض `#DIV/0!` للمستخدم، بل تعرض `غير متاح` مع سبب واضح.
- كل بطاقة يمكن النقر عليها لفتح الشاشة الأصلية بتصفية نفس الشهر.
