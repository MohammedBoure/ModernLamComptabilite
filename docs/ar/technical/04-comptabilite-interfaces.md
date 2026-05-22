# 04 - Interfaces Comptabilite

توثق هذه الوثيقة واجهات وحدة المحاسبة: Cloture de Caisse, Caisse, Coffre, Profitabilite, Fournisseurs, Sous-Traitants, Conventions, Presence, Salaires.

## 04.1 Cloture de Caisse

### الهدف

تسجيل مصاريف caisse اليومية وحساب الفرق بين المبلغ الحقيقي والمبلغ الافتراضي القادم من SOFTLAM.

### Tabs الشاشة

| Tab | المحتوى |
| --- | --- |
| Depenses Caisse | جدول المصاريف الخارجة من الصندوق |
| Differences | مقارنة Montant Reel وMontant Virtuelle |
| Etat Differences | ملخص الفروقات حسب المستخدم |

### جدول Depenses Caisse

الأعمدة:

- Date
- Designation
- Montant
- Piece jointe اختيارية
- Remarque
- Cree par

الأفعال:

- إضافة سطر مصروف.
- تعديل مصروف قبل غلق الشهر.
- حذف مصروف مع سبب.
- عرض مجموع المصاريف.

### جدول Differences

الأعمدة:

- Date
- Utilisateur
- Montant Reel
- Montant Virtuelle
- Difference
- Net
- Remarques

القواعد:

- `Difference = Montant Reel - Montant Virtuelle`
- `Net` هو مجموع الفروقات للمستخدم أو الفترة حسب طريقة العرض.
- إذا كان الفرق لا يساوي صفر، يجب أن يطلب النظام ملاحظة أو تبرير.

### Etat Differences

يعرض ملخصا:

- Utilisateur
- Montant Total
- Nombre de jours avec difference
- Derniere difference

### تحقق الحفظ

لا يسمح بالحفظ إذا:

- التاريخ خارج الشهر المختار.
- المبلغ الحقيقي أو الافتراضي فارغ في سجل difference.
- الفرق غير صفر ولا توجد ملاحظة.

## 04.2 Caisse & Coffre

### الهدف

تتبع حركة الصندوق والخزنة خلال الشهر وحساب المجاميع الشهرية.

### واجهة Mouvement Caisse

الأعمدة:

- Date
- Caisse CV
- Caisse C
- TPE
- Depenses
- Remboursement
- Convention
- Sous-Traitants
- Total

صفوف الحساب:

- Total
- Min (-Ven)
- Max (-Ven)
- Moyenne (-Ven)

القواعد:

- `Total` اليومي يحسب من أعمدة اليوم.
- `Moyenne` لا تعرض خطأ قسمة على صفر، بل تعرض `غير متاح`.
- الجمعة يمكن أن تعامل كحالة خاصة إذا كان التقرير يعتمد `-Ven`.

### واجهة Entrees Supplementaires

الأعمدة:

- Date
- Montant
- Detail
- Statut paiement
- Remarque

القواعد:

- تدخل في Coffre Net Reel فقط إذا كانت payee/validee حسب القرار النهائي.

### واجهة Mouvement Profitabilite

الأعمدة:

- Date
- Montant
- Detail
- Mois source
- Mois destination

الغرض:

- تسجيل الربحية المرحلة من شهر سابق.
- تسجيل أين صرفت الربحية.

ملاحظة من التقرير:

- جدول Mouvement Profitabilite يجب أن يدمج مع جدول Profitabilite Reel حتى يكون مصدر واحد للربحية المرحلة والمصروفة.

### واجهة Sorties Coffre

الأعمدة:

- Date
- Designation
- Montant
- Categorie
- Piece jointe
- Remarque

القواعد:

- تدخل في `Coffre Net Reel` كقيمة سالبة.
- لا يمكن حذفها بعد غلق الشهر إلا بصلاحية admin.

### واجهة Resume Coffre

تعرض:

- Coffre Net Reel
- Chiffre d'affaire LAM
- Chiffre d'affaire Convention
- Chiffre d'affaire ST
- Chiffre d'affaire Entrees Supplementaires
- Chiffre d'Affaire Globale

## 04.3 Bilan Mensuel

### الهدف

عرض نتيجة الشهر وتجميع كل المدخلات المالية في شاشة واحدة.

### أقسام الشاشة

| القسم | الحقول |
| --- | --- |
| Resultat du mois | Caisse CV, Caisse C, Convention, Sous-Traitance, Entrees Supplementaires |
| Prelevements | Total Prelev CV, Total Prelev C, Total Prelev S/T, Total Prelev |
| Rentabilite | Chiffre d'Affaire, Depenses, Profitabilite |
| Investissements | Investissements, Profitabilite Net |

### قواعد العرض

- الشاشة قراءة فقط في الغالب لأنها تجمع بيانات من شاشات أخرى.
- يمكن إضافة زر `Recalculer` لإعادة احتساب المجاميع.
- كل رقم يجب أن يفتح مصدره عند النقر عليه.

## 04.4 Fournisseurs

### الهدف

تسجيل مصاريف الموردين والفواتير والمدفوعات حسب الفئات الموجودة في التقرير.

### الفئات

- Reactifs & Consommables
- Sous-Traitances
- Impots
- Informatique & Bureautique
- Vehicule de Service
- Location
- Energie Labo
- Depenses Internes
- Salaires
- Transport Sous-Traitants
- Autres Depenses
- Investissement

### شاشة Journal des Depenses

الأعمدة:

- Numero
- Categorie
- Fournisseur LAM
- Total des Commandes
- Payer
- Reste
- Date
- Observation

القواعد:

- `Reste = Total des Commandes - Payer`
- إذا كان `Reste = 0` تكون الحالة `Paye`.
- إذا كان `Payer > 0` و`Reste > 0` تكون الحالة `Partiel`.
- إذا كان `Payer = 0` تكون الحالة `Impaye`.

### شاشة تفاصيل Fournisseur

Tabs مقترحة:

- Informations: الاسم، الهاتف، العنوان، نوع المورد.
- Factures: الفواتير والطلبات.
- Paiements: عمليات الدفع.
- Historique: كل تعديل.

## 04.5 Sous-Traitants & Conventions

### الهدف

متابعة المبالغ المستحقة والمدفوعة والباقية للمتعاملين الخارجيين والاتفاقيات.

### جدول Sous-Traitants

الأعمدة:

- Sous-Traitant
- Montant
- Versement
- Date de Reception
- Mode Paiement
- Reste
- Remarques

### جدول Convention

الأعمدة:

- Convention
- Montant
- Versement
- Date de Reception
- Mode Paiement
- Reste
- Remarques

### القواعد

- `Reste = Montant - Versement`
- `Mode Paiement` مطلوب إذا كان `Versement > 0`.
- يمكن أن تكون هناك عدة versements لنفس السجل، لذلك يعتمد التصميم المقترح على تخزين الدفعات في جدول منفصل وربطها بالسجل الأصلي.

## 04.6 Presence

### الهدف

تسجيل حضور الموظفين اليومي خلال الشهر.

### الرموز

| الرمز | المعنى |
| --- | --- |
| P | Present(e) |
| G | Garde Nuit |
| ABS | Absence |
| REC | Recuperation |
| GV-J | Garde Vendredi - Jour |
| GV-N | Garde Vendredi - Nuit |
| P+ | Presence en + / HS |
| C.M | Conge Maladie |
| C | Conge |
| Non Considere | يوم غير محتسب |

### شكل الجدول

الأعمدة:

- Numero
- Employer
- Jour/Garde
- أيام الشهر من 1 إلى 31
- Remarques

لكل موظف يمكن عرض سطرين:

- JOUR
- GARDE

### قواعد الإدخال

- لا يسمح برمز غير معرف.
- لا يسمح بإدخال يوم خارج عدد أيام الشهر.
- أيام الجمعة يمكن تمييزها بلون أو label.
- يمكن نسخ presence من الشهر السابق كقالب أسماء فقط.

## 04.7 Rapport de Salaire

### الهدف

حساب الرواتب الشهرية اعتمادا على الحضور والغياب والحوافز والخصومات.

### الأعمدة

- Numero
- Personne
- Poste
- Salaire Net
- Presence en + / HS
- Deplacement LAM
- Garde Nuit
- Garde Vendredi - Jour
- Garde Vendredi - Nuit
- Absence
- Prime
- Conge
- Penalites
- Avances
- Salaire
- Remarque

### القواعد

- القيم المرتبطة بالحضور يمكن حسابها من جدول Presence.
- Prime, Penalites, Avances يمكن إدخالها يدويا مع سبب.
- المعادلة الدقيقة للراتب النهائي تحتاج تأكيد من الإدارة قبل التنفيذ.
- بعد اعتماد الرواتب، يمكن توليد مصروف في Fournisseurs/Depenses تحت فئة Salaires إذا كان هذا هو سير العمل المطلوب.

### حالات التقرير

| الحالة | المعنى |
| --- | --- |
| Brouillon | الرواتب محسوبة لكن غير مؤكدة |
| Valide | تم اعتماد التقرير |
| Paye | تم دفع الرواتب |
| Verrouille | مقفل بعد غلق الشهر |
