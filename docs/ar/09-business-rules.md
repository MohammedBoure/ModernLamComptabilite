# 09 - Regles Metier et Calculs

توثق هذه الوثيقة القواعد الحسابية والمنطقية المطلوب تنفيذها. بعض القواعد مؤكدة من التقرير، وبعضها مقترح ويحتاج تأكيدا وظيفيا.

## 09.1 Caisse

### Difference

```text
Difference = Montant Reel - Montant Virtuelle
```

### Net

```text
Net = Somme(Difference)
```

قواعد:

- إذا كانت Difference لا تساوي صفر، يجب إدخال Remarque.
- الفروقات تجمع حسب المستخدم وحسب الشهر.
- لا تدخل الفروقات تلقائيا كربح أو خسارة إلا إذا قررت الإدارة ذلك.

## 09.2 Fournisseurs

```text
Reste = Total des Commandes - Payer
```

الحالة:

- `Paye` إذا `Reste = 0`.
- `Partiel` إذا `Payer > 0` و`Reste > 0`.
- `Impaye` إذا `Payer = 0`.

قواعد:

- لا يسمح بأن يكون `Payer > Total des Commandes` إلا كحالة avance واضحة.
- كل دفع يجب أن يحمل Date وMode Paiement.

## 09.3 Sous-Traitants et Conventions

```text
Reste = Montant - Versement
```

قواعد:

- إذا كان versement موجودا يجب اختيار mode paiement.
- إذا كان reste يساوي صفر، الحالة Paye.
- إذا تم الدفع على دفعات، تجمع الدفعات في payments.

## 09.4 Coffre Net Reel

المعادلة من التقرير:

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

نقاط يجب تثبيتها:

- هل Caisse CV وCaisse C تؤخذ من mouvement caisse أم من cloture caisse؟
- هل sous-traitants وconventions تدخل عند الاستلام أم عند الدفع؟
- هل Entrees Supplementaires تدخل فقط إذا كانت payee؟

## 09.5 Chiffre d'Affaires

المعادلة الواضحة:

```text
Chiffre d'Affaires Global =
  Coffre Net Reel
  + Chiffre d'Affaires LAM
  + Chiffre d'Affaires Convention
  + Chiffre d'Affaires ST
  + Chiffre d'Affaires Entrees Supplementaires
```

نقطة غامضة من التقرير:

```text
Chiffre d'affaires LAM = Caisse C + Caisse C + Depenses
```

هذه الصيغة تحتاج تأكيدا وظيفيا لأنها تبدو وكأن `Caisse C` مكررة. الاحتمالات المطلوب حسمها:

- Caisse CV + Caisse C + Depenses
- أو Caisse C + TPE + Depenses
- أو صيغة أخرى.

## 09.6 Profitabilite

من جدول bilan:

```text
Profitabilite = Chiffre d'Affaire - Depenses
```

من التقرير:

```text
Profitabilite reelle =
  Profitabilite du mois actuel
  + Reste profitabilite des mois decales vers ce mois
```

بعد الاستثمارات:

```text
Profitabilite Net Apres Investissements =
  Profitabilite - Investissements
```

النسبة:

```text
% Profitabilite = Profitabilite / Chiffre d'Affaire
% Profitabilite Net = Profitabilite Net / Chiffre d'Affaire
```

قاعدة تقنية:

- إذا كان Chiffre d'Affaire يساوي صفر، لا تعرض خطأ قسمة على صفر.

## 09.7 Presence

الرموز المعتمدة:

- P
- G
- ABS
- REC
- GV-J
- GV-N
- P+
- C.M
- C
- Non Considere

قواعد:

- رمز واحد فقط لكل خانة يوم/موظف.
- يمكن أن يكون للموظف سطر JOUR وسطر GARDE.
- الأيام غير المحتسبة لا تدخل في salary calculation.

## 09.8 Salaires

المعادلة النهائية تحتاج تأكيد، لكن التصور الأولي:

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

نقاط تحتاج قرار:

- هل Conge يخصم أم لا؟
- هل Conge Maladie يخصم؟
- هل Absence تدخل كعدد أيام أم مبلغ؟
- أسعار garde nuit وgarde vendredi هل ثابتة أم حسب الموظف؟

## 09.9 Conges

من التقرير:

```text
Jours de Conge = Jours de conge + 2.5 chaque mois de travail
```

قاعدة تاريخ التوظيف كما وردت:

- إذا `date d'embauche < 15`، الشهر الأول غير محتسب.
- وإلا، الشهر الأول محتسب.

تنبيه:

- يجب تأكيد هذه القاعدة قبل التنفيذ لأنها تؤثر مباشرة على حقوق الموظفين.

## 09.10 Etat d'Encaissement

قواعد:

- يولد صف لكل يوم في الشهر.
- تاريخ كل صف مطابق لليوم.
- designation الافتراضي `DIVERS CLIENTS`.
- مجموع الشهر يظهر في الأسفل.
- التقرير يحتوي cachet et signature.

## 09.11 غلق الشهر

لا يغلق الشهر إذا:

- توجد فروقات غير مبررة.
- توجد رواتب Brouillon.
- يوجد bilan غير محسوب.
- توجد عمليات مالية Brouillon.

بعد الغلق:

- يمنع التعديل العادي.
- يسمح بالطباعة.
- يسمح بالتعديل الاستثنائي فقط مع audit log.
