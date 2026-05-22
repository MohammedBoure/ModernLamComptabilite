# 06 - Interfaces DRH

وحدة DRH تجمع الموظفين، العقود، والعطل في مكان واحد. التقرير يذكر صراحة أن الجداول الثلاثة يجب دمجها، لذلك التصميم المقترح هو شاشة موظف موحدة مع Tabs.

## 06.1 Liste Employes

### الهدف

عرض كل الموظفين والبحث عنهم بسرعة.

### الأعمدة

- Numero
- Nom/Prenom
- Fonction
- Date Naissance
- Age
- Telephone 01
- Telephone 02
- Statut
- Contrat actif
- Conge 2025/2026

### الفلاتر

- Fonction
- Statut: actif, suspendu, demissionne
- Contrat: actif, expire, sans contrat
- Recherche par nom

### الأفعال

- Ajouter employe
- Ouvrir fiche
- Exporter liste
- Imprimer fiche

## 06.2 Fiche Employe

### Tabs

| Tab | المحتوى |
| --- | --- |
| Identite | المعلومات الشخصية |
| Contrat | التوظيف والعقد وCNAS |
| Conges | رصيد العطل |
| Presence | حضور الموظف حسب الشهر |
| Salaires | رواتب الموظف |
| Documents | ملفات مرفقة |
| Historique | تعديلات الملف |

## 06.3 Identite

الحقول:

- Nom/Prenom
- Fonction
- Date Naissance
- Age محسوب تلقائيا
- Lieu de Naissance
- Adresse
- Num Telephone 01
- Num Telephone 02
- Numero SS
- Numero ANEM
- Remarque

قواعد:

- Age لا يدخل يدويا، يحسب من Date Naissance.
- رقم SS وANEM يمكن تركهما فارغين في البداية، لكن يظهر تنبيه نقص بيانات.

## 06.4 Contrat

الحقول:

- Date d'Embauche
- Date d'Inscription CNAS
- Contrat
- Du
- Au
- Demission
- Statut contrat
- Remarque

قواعد:

- لا يسمح بعقد له `Au` قبل `Du`.
- إذا كان `Au` مر قبل تاريخ اليوم، يظهر العقد `Expire`.
- إذا وجدت `Demission` يصبح الموظف غير نشط ابتداء من ذلك التاريخ.
- يمكن حفظ عدة عقود تاريخية لنفس الموظف، لكن عقد واحد فقط يكون actif.

## 06.5 Conges

الحقول:

- Annee
- Nom/Prenom
- Fonction
- Date d'Embauche
- Conge annee courante jours
- Jours pris
- Reste conge
- Remarque

القواعد المعروفة من التقرير:

- يضاف `2.5` يوم لكل شهر عمل.
- إذا كان تاريخ التوظيف قبل 15، الشهر الأول غير محتسب حسب التقرير.
- وإلا الشهر الأول محتسب.

نقطة تحتاج تأكيد:

- القاعدة المعتادة في بعض المؤسسات قد تكون بالعكس، لذلك يجب تثبيت قاعدة ModernLam رسميا قبل التنفيذ.

## 06.6 Presence Employe

داخل fiche employe يمكن عرض حضور موظف واحد:

- اختيار الشهر والسنة.
- جدول أيام الشهر.
- الرموز P, ABS, G, GV-J, GV-N, C, C.M, REC, P+.
- مجموع أيام الحضور والغياب والعطل.

هذه الشاشة للقراءة السريعة، أما الإدخال الجماعي يكون في شاشة Presence العامة.

## 06.7 Salaires Employe

يعرض تاريخ رواتب الموظف:

- Mois
- Salaire Net
- Primes
- Penalites
- Avances
- Absences
- Salaire final
- Statut paiement

يمكن فتح تقرير الراتب الشهري من هنا.

## 06.8 Documents

ملفات اختيارية:

- Carte identite
- Contrat signe
- Attestation CNAS
- Documents ANEM
- Certificat medical
- Autres

كل ملف يجب أن يحمل:

- Nom
- Type
- Date ajout
- Ajoute par
- Remarque

## 06.9 تنبيهات DRH

أمثلة:

- موظف بدون تاريخ ميلاد.
- موظف بدون عقد نشط.
- عقد ينتهي خلال 30 يوم.
- موظف بدون CNAS.
- رصيد عطلة سالب.
- أيام عطلة مدخلة أكبر من الرصيد.
