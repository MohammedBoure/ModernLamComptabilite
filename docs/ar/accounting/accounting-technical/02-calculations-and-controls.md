# 02 - الحسابات والضوابط المحاسبية

توضح هذه الوثيقة الحسابات والضوابط التي تظهر للمحاسبة والإدارة المالية. الصياغة هنا وظيفية ومحاسبية، وليست تقنية برمجية داخلية.

## Cloture Caisse

### حساب الفرق

```text
Difference = Montant Reel - Montant Virtuelle
```

| الحالة | المعنى | الإجراء |
| --- | --- | --- |
| Difference = 0 | لا يوجد فرق | تحفظ العملية دون تنبيه. |
| Difference > 0 | المبلغ الحقيقي أكبر من SOFTLAM | تظهر قيمة موجبة مع ملاحظة توضيحية. |
| Difference < 0 | المبلغ الحقيقي أقل من SOFTLAM | تظهر قيمة سالبة مع ملاحظة توضيحية. |

ضوابط:

- Remarque مطلوبة عند وجود فرق.
- كل فرق يظهر في Etat Differences.
- الفروقات تجمع حسب المستخدم وحسب الشهر.

## Fournisseurs

### حساب الباقي

```text
Reste = Total des Commandes - Payer
```

| الحالة | الشرط | المعنى |
| --- | --- | --- |
| Impaye | Payer = 0 | لم يتم الدفع. |
| Partiel | Payer > 0 و Reste > 0 | دفع جزئي. |
| Paye | Reste = 0 | دفع كامل. |

ضوابط:

- Mode Paiement مطلوب عند وجود دفع.
- Observation تحفظ عند وجود توضيح خاص.
- الدفع الجزئي يبقى ظاهرا إلى غاية تسوية الباقي.

## Sous-Traitants وConventions

### حساب الباقي

```text
Reste = Montant - Versement
```

ضوابط:

- Date de Reception تحفظ لمتابعة تاريخ الاستلام.
- Mode Paiement مطلوب عند تسجيل versement.
- reste يظهر في Etat Sous-Traitants أو Etat Convention.

## Coffre Net Reel

الصيغة الوظيفية:

```text
Coffre Net Reel =
  Caisse CV
  + Caisse C
  + Entrees Supplementaires payees
  + Mouvement Profitabilite
  + Sous-Traitants payes
  + Convention payee
  - Sortie Coffre
```

ضوابط:

- Sorties Coffre تخصم من صافي الخزنة.
- Entrees Supplementaires تدخل حسب حالة الدفع المعتمدة.
- أي قيمة غير واضحة يجب أن تبقى قابلة للتتبع من الشاشة الأصلية.

## Bilan Mensuel

المؤشرات الأساسية:

| المؤشر | المعنى |
| --- | --- |
| Chiffre d'Affaire | رقم الأعمال الشهري. |
| Depenses | مجموع المصاريف. |
| Profitabilite | الربحية قبل الاستثمارات. |
| Investissements | الاستثمارات. |
| Profitabilite Net | الربحية بعد الاستثمارات. |

صيغة الربحية:

```text
Profitabilite = Chiffre d'Affaire - Depenses
```

صيغة الربحية بعد الاستثمارات:

```text
Profitabilite Net = Profitabilite - Investissements
```

ضوابط:

- لا تعرض النسب عند غياب رقم الأعمال أو مساواته للصفر.
- كل رقم في البيلان يجب أن يكون له مصدر واضح في الشاشات الأصلية.

## Presence

الرموز المعتمدة:

| الرمز | المعنى |
| --- | --- |
| P | حاضر. |
| ABS | غياب. |
| G | Garde Nuit. |
| GV-J | Garde Vendredi Jour. |
| GV-N | Garde Vendredi Nuit. |
| C | عطلة. |
| C.M | عطلة مرضية. |
| REC | Recuperation. |
| P+ | Presence en + / HS. |

ضوابط:

- الرموز غير المعتمدة لا تدخل في الحساب.
- كل يوم من الشهر يرتبط برمز واضح أو يبقى فارغا حسب سياسة الإدخال.

## Salaires

الصيغة الوظيفية الأولية:

```text
Salaire Final =
  Salaire Net
  + Presence en + / HS
  + Deplacement LAM
  + Garde Nuit
  + Garde Vendredi Jour
  + Garde Vendredi Nuit
  + Prime
  - Absence
  - Penalites
  - Avances
```

ضوابط:

- Prime وPenalites وAvances تحفظ مع ملاحظة عند الحاجة.
- Rapport de Salaire يبقى Brouillon قبل الاعتماد.
- بعد الاعتماد يصبح التقرير Valide.
- بعد الدفع تصبح الحالة Paye.

## Conges

قاعدة اكتساب العطل:

```text
Jours de Conge = Jours de conge + 2.5 chaque mois de travail
```

ضوابط:

- Date d'Embauche تستعمل في حساب رصيد العطل.
- Jours Pris تخصم من Jours Acquis.
- Reste يمثل الرصيد المتبقي.

## Etat d'Encaissement

ضوابط:

- يولد التقرير صفا لكل يوم من أيام الشهر.
- designation الافتراضي يمكن أن يكون `DIVERS CLIENTS`.
- total الشهر يظهر في أسفل التقرير.
- النسخة الرسمية تحتوي على cachet et signature.
