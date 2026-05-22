# التوثيق العربي - ModernLam Comptabilite

هذا هو الفهرس المحلي للتوثيق العربي. النسخة العربية هي النسخة الأساسية التي سنطورها حاليا، ثم نستعملها لاحقا كأساس للترجمة إلى الفرنسية والإنجليزية.

## التقرير المرجعي

| النوع | الملف | الملاحظات |
| --- | --- | --- |
| التقرير الرئيسي | [Rapport Logiciel Comptabilite PDF](<../../Rapport Logiciel Comptabilité_720ec9a3-2c6d-4f36-87b8-5ecbc04ea00e.pdf>) | المصدر الأصلي للجداول والوحدات والمعادلات. |

## ملفات التوثيق العربية

| الملف | المحتوى |
| --- | --- |
| [01-product-overview.md](./01-product-overview.md) | الرؤية العامة، المستخدمون، حدود النسخة الأولى، ومبادئ البرنامج. |
| [02-navigation-and-layout.md](./02-navigation-and-layout.md) | شكل التنقل، القائمة الجانبية، مكونات الشاشات المشتركة، والطباعة. |
| [03-dashboard.md](./03-dashboard.md) | تفاصيل لوحة التحكم الشهرية والتنبيهات والاختصارات. |
| [04-comptabilite-interfaces.md](./04-comptabilite-interfaces.md) | كل واجهات المحاسبة: caisse, coffre, fournisseurs, presence, salaires. |
| [05-etats-interfaces.md](./05-etats-interfaces.md) | واجهات Etats والتقارير: fournisseurs, sous-traitants, vehicule, cheques, encaissement. |
| [06-drh-interfaces.md](./06-drh-interfaces.md) | واجهات DRH: الموظفون، العقود، العطل، ملفات الموظف. |
| [07-workflows.md](./07-workflows.md) | سير العمل اليومي والشهري وغلق الشهر والترحيل. |
| [08-data-model.md](./08-data-model.md) | تصور قاعدة البيانات والعلاقات الأساسية. |
| [09-business-rules.md](./09-business-rules.md) | القواعد الحسابية والمنطقية المؤكدة والمفتوحة. |
| [10-permissions-and-audit.md](./10-permissions-and-audit.md) | الصلاحيات، الأمان، وسجل التعديلات. |
| [11-reporting-and-printing.md](./11-reporting-and-printing.md) | الطباعة، PDF، Excel، وسجل التقارير الرسمية. |
| [12-implementation-roadmap.md](./12-implementation-roadmap.md) | خطة تنفيذ مرحلية من MVP إلى نسخة كاملة. |
| [13-open-questions.md](./13-open-questions.md) | الأسئلة التي يجب تأكيدها قبل البرمجة النهائية. |

## طريقة القراءة المقترحة

1. ابدأ بـ [01-product-overview.md](./01-product-overview.md) لفهم المنتج.
2. اقرأ [02-navigation-and-layout.md](./02-navigation-and-layout.md) لفهم شكل البرنامج والتنقل.
3. راجع [04-comptabilite-interfaces.md](./04-comptabilite-interfaces.md)، [05-etats-interfaces.md](./05-etats-interfaces.md)، و[06-drh-interfaces.md](./06-drh-interfaces.md) لفهم الواجهات.
4. استعمل [07-workflows.md](./07-workflows.md) لفهم سير العمل اليومي والشهري.
5. استعمل [08-data-model.md](./08-data-model.md) و[09-business-rules.md](./09-business-rules.md) عند بداية التصميم البرمجي.
6. اجمع الإجابات على [13-open-questions.md](./13-open-questions.md) قبل تثبيت الحسابات النهائية.

## ملاحظات تنظيمية

- أي تغيير في القواعد الحسابية يجب تحديثه في [09-business-rules.md](./09-business-rules.md).
- أي تغيير في شاشة يجب تحديثه في ملف الواجهات المناسب.
- أي قرار جديد من الإدارة يجب أن ينعكس في ملف الأسئلة المفتوحة أو في ملف القواعد.
