# التوثيق العربي - ModernLam Comptabilite

يجمع الفهرس المحلي التوثيق العربي الخاص ببرنامج ModernLam Comptabilite. النسخة العربية هي النسخة التفصيلية الأساسية حاليا، وتشكل مرجعا لاحقا للترجمة إلى الفرنسية والإنجليزية.

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

## ترتيب القراءة المرجعي

| الترتيب | الملف | الغرض |
| --- | --- | --- |
| 1 | [01-product-overview.md](./01-product-overview.md) | فهم المنتج وحدوده ومستخدميه. |
| 2 | [02-navigation-and-layout.md](./02-navigation-and-layout.md) | فهم بنية البرنامج والتنقل العام. |
| 3 | [04-comptabilite-interfaces.md](./04-comptabilite-interfaces.md) | فهم واجهات المحاسبة الأساسية. |
| 4 | [05-etats-interfaces.md](./05-etats-interfaces.md) | فهم واجهات التقارير والحالات. |
| 5 | [06-drh-interfaces.md](./06-drh-interfaces.md) | فهم واجهات الموارد البشرية. |
| 6 | [07-workflows.md](./07-workflows.md) | فهم سير العمل اليومي والشهري. |
| 7 | [08-data-model.md](./08-data-model.md) | مرجع تصميم قاعدة البيانات. |
| 8 | [09-business-rules.md](./09-business-rules.md) | مرجع القواعد الحسابية والمنطقية. |
| 9 | [13-open-questions.md](./13-open-questions.md) | قائمة القرارات التي تحتاج تأكيدا قبل تثبيت الحسابات النهائية. |

## ملاحظات تنظيمية

- أي تغيير في القواعد الحسابية يتطلب تحديث [09-business-rules.md](./09-business-rules.md).
- أي تغيير في شاشة يتطلب تحديث ملف الواجهات المناسب.
- أي قرار إداري جديد يجب أن ينعكس في ملف الأسئلة المفتوحة أو في ملف القواعد.
