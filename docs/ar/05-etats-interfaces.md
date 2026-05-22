# 05 - Interfaces Etats et Rapports

وحدة Etats مخصصة للمتابعة والطباعة. أغلب شاشاتها قراءة وتجميع، لكنها يمكن أن تحتوي على إدخالات مساعدة مثل الشيكات أو مصاريف السيارة.

## مبادئ التقارير

كل تقرير يجب أن يدعم:

- اختيار الشهر أو السنة.
- البحث والفلترة.
- الطباعة.
- تصدير PDF.
- تصدير Excel.
- عرض تاريخ الإنشاء واسم المستخدم.

## 05.1 Etat Fournisseurs

### الهدف

عرض حالة الموردين: إجمالي المبالغ، المدفوع، والباقي، مع إمكانية الدخول إلى تفاصيل كل مورد.

### أقسام الشاشة

- Total Fournisseurs
- Total Equipements
- Total Consommables
- Fournisseur ASD
- Fournisseur SARL ALMED
- أي مورد آخر يضاف لاحقا

### الأعمدة

في الملخص:

- Fournisseur
- Montant
- Versement
- Reste

في التفاصيل:

- Date
- Mois paiement
- Montant BL Achat / Montant Facture Achat
- Versement
- Paiement
- Observation

### القواعد

- `Reste = Montant - Versement`
- يجب تلوين `Reste > 0`.
- يمكن فلترة التقرير حسب fournisseur أو categorie.

## 05.2 Etat Sous-Traitants

### الهدف

تقديم رؤية شاملة على كل sous-traitants وconventions.

### أقسام الشاشة

- Tous (Sous-Traitants/Conventions)
- Sous-Traitants
- Conventions
- تفاصيل كل متعامل خارجي

### الأعمدة

- ID
- Nom
- Montant
- Versement
- Reste
- Date
- Paiement
- Observation

### سلوك الشاشة

- الضغط على اسم متعامل يفتح صفحة تفاصيله.
- يمكن عرض كل الدفعات المرتبطة به.
- يجب إظهار `Total reste a payer` بوضوح.

## 05.3 Suivi Vehicule de Service

### الهدف

متابعة مصاريف السيارة والكيلومترات واستهلاك الوقود.

### الأعمدة

- Date
- Montant
- Details
- Kilometrage
- GPL / Kilometre en +
- Essence / Kilometre en +

### المجاميع

- Total montant
- Total GPL
- Total Essence
- Moyenne KM/Plein

### القواعد

- لا تعرض `#DIV/0!` عند عدم وجود بيانات، بل `غير متاح`.
- إذا أدخل المستخدم kilometrage أقل من السابق، يظهر تحذير.
- يمكن ربط مصاريف السيارة بفئة `Vehicule de Service` في Fournisseurs أو Sorties Coffre حسب القرار.

## 05.4 Suivi Compte SGA / Etat de Cheques

### الهدف

تتبع حساب SGA والشيكات خلال السنة.

### الحقول العليا

- Montant du Compte le 31/12/annee precedente
- Montant du Compte le date actuelle
- Annee

### الأعمدة

- Numero
- La Date
- Beneficiaire
- Numero Cheque
- Montant
- Entrees
- Sorties
- Designation
- Mois

### القواعد

- `Entrees` تزيد الرصيد.
- `Sorties` تنقص الرصيد.
- يمكن حساب الرصيد الجاري بعد كل عملية في نسخة متقدمة.
- رقم الشيك يجب أن يكون فريدا إذا كان النوع Sortie par cheque.

### العرض السنوي

الشاشة تعرض السنة مقسمة بصريا حسب الأشهر:

- janvier
- fevrier
- mars
- avril
- mai
- juin
- juillet
- باقي الأشهر حسب السنة المختارة

## 05.5 Etat d'Encaissement

### الهدف

إعداد جدول شهري للطباعة خاص بالتصريح الضريبي.

### رأس التقرير

يحتوي على:

- Logo ModernLam
- Nom du laboratoire
- NIF
- RIP
- Jijel le: تاريخ الطباعة
- Etat d'Encaissement mois de: الشهر والسنة

### الأعمدة

- Numero
- Date
- Designation
- Observations
- Montants

### القواعد

- يولد النظام صفا لكل يوم من أيام الشهر.
- designation الافتراضي يمكن أن يكون `DIVERS CLIENTS`.
- Montants يمكن أن تأتي من caisse أو تدخل يدويا حسب قرار الإدارة.
- في الأسفل: Total + Cachet et signature.

### الطباعة

هذا التقرير يجب أن يكون قابلا للطباعة بشكل رسمي، لذلك يحتاج:

- حجم صفحة A4.
- هوامش ثابتة.
- Header مطابق لهوية المخبر.
- جدول لا ينقسم بطريقة غير مقروءة.

## 05.6 Exports

كل تقرير يوفر:

- `PDF officiel` للطباعة والأرشفة.
- `Excel` للمراجعة والتحليل.
- `CSV` اختياريا للاستيراد في أدوات أخرى.

أسماء الملفات المقترحة:

- `etat-fournisseurs-2026-02.pdf`
- `etat-sous-traitants-2026-02.xlsx`
- `encaissement-2026-01.pdf`
- `etat-cheques-2026.pdf`

## 05.7 Historique des Rapports

يفضل حفظ سجل لكل عملية طباعة أو تصدير:

- نوع التقرير.
- الفترة.
- المستخدم.
- التاريخ.
- format.
- هل التقرير رسمي أم draft.
