# ModernLam - Logiciel de Comptabilite

هذا المستودع مخصص لبناء برنامج محاسبة وتسيير داخلي لمخبر **ModernLam - Laboratoire d'Analyses Medicales**، اعتمادا على التقرير المرجعي الموجود في هذا المجلد.

الهدف من البرنامج هو تحويل الجداول اليدوية/Excel الموجودة في التقرير إلى تطبيق واضح ومنظم يساعد في متابعة الصندوق، الخزنة، الموردين، sous-traitants، conventions، الحضور، الرواتب، التقارير المالية، وملفات الموارد البشرية.

## التقارير المرجعية

هذه الملفات هي نقطة الانطلاق لفهم البرنامج المطلوب:

| النوع | الملف | الملاحظات |
| --- | --- | --- |
| التقرير الرئيسي | [Rapport Logiciel Comptabilite PDF](<./Rapport Logiciel Comptabilité_720ec9a3-2c6d-4f36-87b8-5ecbc04ea00e.pdf>) | يحتوي على الجداول، الوحدات، المعادلات، وملاحظات الدمج المطلوبة. |
| فهرس تقارير docs | [docs/README.md](./docs/README.md) | مكان مخصص لروابط التقارير والوثائق الإضافية التي ستضاف لاحقا داخل `docs/`. |

> حاليا يوجد تقرير PDF واحد فقط في جذر المشروع. تم تفصيله إلى ملفات توثيق شاملة داخل `docs/`.

## التوثيق التفصيلي

تم تقسيم مواصفات البرنامج إلى عدة ملفات حتى تكون قابلة للمراجعة والتنفيذ:

- [Vision generale](./docs/01-product-overview.md)
- [Navigation et structure des ecrans](./docs/02-navigation-and-layout.md)
- [Tableau de bord](./docs/03-dashboard.md)
- [Interfaces Comptabilite](./docs/04-comptabilite-interfaces.md)
- [Interfaces Etats](./docs/05-etats-interfaces.md)
- [Interfaces DRH](./docs/06-drh-interfaces.md)
- [Workflows fonctionnels](./docs/07-workflows.md)
- [Modele de donnees](./docs/08-data-model.md)
- [Regles metier et calculs](./docs/09-business-rules.md)
- [Permissions et audit](./docs/10-permissions-and-audit.md)
- [Reporting et impression](./docs/11-reporting-and-printing.md)
- [Plan d'implementation](./docs/12-implementation-roadmap.md)
- [Questions ouvertes](./docs/13-open-questions.md)

## فكرة البرنامج

سيكون البرنامج تطبيقا داخليا ينظم العمل المحاسبي والاداري للمخبر بدل الاعتماد على جداول منفصلة. الفكرة الأساسية هي أن كل عملية مالية أو ادارية تدخل مرة واحدة، ثم تظهر في التقارير الشهرية والسنوية المناسبة تلقائيا.

البرنامج يجب أن يوفر:

- إدخال يومي لحركة الصندوق والخزنة.
- حساب الفروقات بين المبلغ الحقيقي ومبلغ SOFTLAM.
- متابعة المدفوعات والبواقي للموردين، sous-traitants، وconventions.
- حساب الربحية الشهرية وترحيل باقي الربحية بين الشهور.
- متابعة الحضور، الغيابات، gardes، العطل، والرواتب.
- إنشاء حالات وتقارير قابلة للطباعة أو التصدير.
- إدارة ملف الموظفين والعقود والعطل في قاعدة واحدة.

## الوحدات الرئيسية

### 1. Comptabilite

هذه هي الوحدة الأساسية للبرنامج، وتضم:

- **Cloture de Caisse**: تسجيل مصاريف الصندوق، إدخال مبلغ الصندوق الحقيقي، مقارنة المبلغ الحقيقي مع مبلغ SOFTLAM، وحساب الفروقات حسب المستخدم.
- **Caisse & Coffre**: متابعة حركة الصندوق، مداخيل caisse CV وcaisse C وTPE، المصاريف، remboursements، conventions، sous-traitants، والمجاميع الشهرية.
- **Entrees Supplementaires**: تسجيل المداخيل الاضافية مع التاريخ، المبلغ، والتفاصيل.
- **Mouvement Profitabilite**: متابعة استعمال الربحية أو ترحيلها بين الشهور.
- **Sorties Coffre**: تسجيل المبالغ الخارجة من الخزنة مع التاريخ، التسمية، والمبلغ.
- **Bilan Mensuel**: حساب النتيجة الشهرية، chiffre d'affaires، depenses، profitabilite، investissements، والربحية الصافية بعد الاستثمارات.
- **Fournisseurs**: متابعة فواتير ومصاريف الموردين حسب الفئات: reactifs, consommables, sous-traitances, impots, informatique, vehicule, location, energie, salaires, transport, autres depenses, investissements.
- **Sous-Traitants & Conventions**: متابعة المبلغ، versement، تاريخ الاستلام، طريقة الدفع، الباقي، والملاحظات.
- **Presence**: تسجيل الحضور اليومي، الغياب، garde nuit، garde vendredi jour/nuit، conge، recuperation، والايام غير المحتسبة.
- **Rapport de Salaire**: حساب الراتب اعتمادا على الراتب الصافي، الحضور الاضافي، التنقل، gardes، الغيابات، primes، conges، penalites، avances، والملاحظات.

### 2. Etats

هذه الوحدة مخصصة للتقارير والحالات:

- **Etat Fournisseurs**: ملخص الموردين حسب المبالغ، المدفوع، والباقي، مع تفاصيل الموردين مثل ASD وSARL ALMED.
- **Etat Sous-Traitants**: ملخص sous-traitants وconventions مع تفاصيل الدفع والباقي.
- **Suivi Vehicule de Service**: متابعة مصاريف السيارة، الكيلومترات، GPL، essence، ومتوسط الاستهلاك.
- **Suivi Compte SGA / Etat de Cheques**: متابعة الشيكات، الرصيد الافتتاحي، الرصيد الحالي، المستفيد، رقم الشيك، المداخل، المخارج، والتسمية.
- **Etat d'Encaissement**: جدول شهري قابل للطباعة للتصريح الضريبي، يحتوي على أيام الشهر، الزبائن/التسمية، الملاحظات، والمبالغ.

### 3. Direction des Ressources Humaines (DRH)

هذه الوحدة تجمع بيانات الموظفين والعقود والعطل:

- **Employes**: الاسم واللقب، الوظيفة، تاريخ ومكان الميلاد، السن، العنوان، أرقام الهاتف، رقم الضمان الاجتماعي، ورقم ANEM.
- **Contrats**: تاريخ التوظيف، تاريخ التسجيل CNAS، نوع العقد، مدة العقد، تاريخ البداية والنهاية، والاستقالة/الخروج.
- **Conges**: رصيد العطل السنوي، تاريخ التوظيف، الملاحظات، واحتساب أيام العطلة.

ملاحظة مهمة من التقرير: جداول **Employes** و**Contrats** و**Conges** يجب أن تدمج في جدول أو شاشة واحدة حتى لا تتكرر معلومات الموظف.

## القواعد والمعادلات المعروفة

المعادلات التالية مأخوذة من التقرير وتحتاج أن تتحول إلى منطق داخل البرنامج:

- `Difference = Montant Reel - Montant Virtuelle`
- `Net = Somme(Difference)`
- `Coffre Net Reel = Caisse CV + Caisse C + Entrees Supplementaires payees + Mouvement Profitabilite + Sous-Traitants payes + Convention payee - Sortie Coffre`
- `Chiffre d'affaires globale = Coffre Net Reel + Chiffre d'affaires LAM + Chiffre d'affaires Convention + Chiffre d'affaires ST + Chiffre d'affaires Entrees Supplementaires`
- `Profitabilite reelle = Profitabilite du mois actuel + reste profitabilite des mois decales vers ce mois`
- `Jours de Conge = Jours de conge + 2.5` لكل شهر عمل.

قاعدة العطل المذكورة في التقرير:

- إذا كان `date d'embauche < 15` فإن الشهر الأول غير محتسب.
- وإلا فإن الشهر الأول محتسب.

## نقاط تحتاج تأكيد قبل التنفيذ النهائي

التقرير كاف لبداية المشروع، لكنه يحتاج بعض القرارات قبل بناء نسخة نهائية دقيقة:

- هل بيانات SOFTLAM سيتم إدخالها يدويا أم استيرادها من ملف؟
- هل يمكن تعديل شهر بعد غلقه؟ ومن يملك صلاحية ذلك؟
- ما هي صلاحيات المستخدمين: admin، comptable، caisse، direction، RH؟
- كيف تحسب الرواتب بدقة عند وجود غياب، garde، prime، penalite، avance، conge؟
- هل الدفع الجزئي للموردين وsous-traitants يجب أن يكون له سجل عمليات منفصل؟
- هل كل تعديل مالي يجب أن يحفظ في historique/audit log؟
- صيغة `Chiffre d'affaires LAM` في التقرير تظهر كالتالي: `Caisse C + Caisse C + Depenses`. يجب تأكيدها لأنها قد تحتوي على تكرار غير مقصود.
- يجب تأكيد شكل التقارير المطبوعة: PDF، Excel، أو الاثنين معا.

## تصور تجربة الاستخدام

سيبدأ المستخدم من لوحة شهرية تعرض:

- الشهر والسنة الحالية.
- ملخص caisse/coffre.
- مجموع المداخيل والمصاريف.
- الربحية، الاستثمارات، والباقي.
- تنبيهات حول المدفوعات غير المكتملة، فروقات الصندوق، والعقود/العطل.

ثم يستطيع الانتقال إلى شاشات الادخال:

- شاشة يومية للصندوق.
- شاشة الخزنة.
- شاشة الموردين.
- شاشة sous-traitants/conventions.
- شاشة الحضور.
- شاشة الرواتب.
- شاشة الموظفين والعقود والعطل.
- شاشة التقارير والطباعة.

## تصور قاعدة البيانات كبداية

الكيانات الأولية المقترحة:

- `users`
- `cash_closures`
- `cash_expenses`
- `cash_movements`
- `coffer_movements`
- `additional_entries`
- `profitability_movements`
- `suppliers`
- `supplier_transactions`
- `subcontractors`
- `conventions`
- `payments`
- `employees`
- `employee_contracts`
- `employee_attendance`
- `salary_reports`
- `leave_balances`
- `vehicle_expenses`
- `cheques`
- `encashments`
- `audit_logs`

## خطة بناء أولية

1. تثبيت قاعدة البيانات والنماذج الأساسية.
2. بناء واجهات الادخال الشهرية واليومية.
3. تطبيق المعادلات الحسابية الأساسية.
4. بناء تقارير caisse/coffre والبيلان الشهري.
5. إضافة الموردين، sous-traitants، وconventions.
6. إضافة الحضور والرواتب.
7. إضافة DRH والعطل.
8. إضافة الطباعة والتصدير.
9. إضافة الصلاحيات وhistorique.

## الحالة الحالية

هذه هي الوثيقة الأولى للمشروع. لا يوجد كود تطبيقي بعد، والتقرير الرئيسي هو المصدر الوحيد المؤكد حتى الآن.
