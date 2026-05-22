# التوثيق العربي - ModernLam Comptabilite

يجمع الفهرس المحلي التوثيق العربي الخاص ببرنامج ModernLam Comptabilite. ينقسم التوثيق العربي إلى قسمين: قسم وظيفي موجه للمحاسبة والإدارة، وقسم تقني موجه للتصميم والتنفيذ.

## التقرير المرجعي

| النوع | الملف | الملاحظات |
| --- | --- | --- |
| التقرير الرئيسي | [Rapport Logiciel Comptabilite PDF](<../../Rapport Logiciel Comptabilité_720ec9a3-2c6d-4f36-87b8-5ecbc04ea00e.pdf>) | المصدر الأصلي للجداول والوحدات والمعادلات. |

## أقسام التوثيق

| القسم | الرابط | الجمهور | المحتوى |
| --- | --- | --- | --- |
| توثيق المحاسبة والإدارة | [accounting/README.md](./accounting/README.md) | المحاسبة، الإدارة، الموارد البشرية | توثيق عادي، توثيق محاسبي تقني، وتوثيق شكل الواجهة. |
| التوثيق التقني | [technical/README.md](./technical/README.md) | التصميم، البرمجة، الصيانة | مواصفات تقنية عامة منفصلة عن التوثيق التنفيذي التطبيقي الذي سيملأ بعد اختيار التكنولوجيا. |

## ترتيب القراءة المرجعي

| الترتيب | القسم | الغرض |
| --- | --- | --- |
| 1 | [accounting/general/README.md](./accounting/general/README.md) | فهم البرنامج من منظور العمل المحاسبي والإداري. |
| 2 | [accounting/accounting-technical/README.md](./accounting/accounting-technical/README.md) | معرفة البيانات والحسابات التي يعتمدها البرنامج. |
| 3 | [accounting/ui/README.md](./accounting/ui/README.md) | معرفة شكل الواجهة وتنظيم العناصر داخل الشاشات. |
| 4 | [technical/specification/README.md](./technical/specification/README.md) | قراءة المواصفات التقنية العامة غير المرتبطة بتكنولوجيا محددة. |
| 5 | [technical/implementation/README.md](./technical/implementation/README.md) | معرفة نطاق التوثيق التنفيذي التطبيقي الذي سيملأ لاحقا. |
| 6 | [technical/specification/08-data-model.md](./technical/specification/08-data-model.md) | مرجع نموذج البيانات العام. |

## ملاحظات تنظيمية

- أي تغيير في القواعد الحسابية يتطلب تحديث [technical/specification/09-business-rules.md](./technical/specification/09-business-rules.md) وتحديث القسم الوظيفي المرتبط به عند الحاجة.
- أي تغيير في شاشة يتطلب تحديث ملف الواجهات التقني وملف الشاشات الوظيفي عند الحاجة.
- أي قرار إداري جديد يجب أن ينعكس في ملف القرارات المفتوحة أو في ملف القواعد.
