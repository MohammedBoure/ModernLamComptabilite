# Prototype Expansion Commit Brief

هذا الملف هو مذكرة عمل تفصيلية موجهة إلى Codex عند توسيع نموذج ModernLam web prototype لاحقا.

## الهدف العام

توسيع الـ prototype بحيث يبقى شاملا لكل ما هو موجود في التوثيق، مع تحسين تجربة المستخدم قدر الإمكان، مع الحفاظ على طبيعته الحالية:

- يعمل مباشرة من `index.html`.
- لا يحتاج backend أو database.
- يخزن البيانات في المتصفح عبر `localStorage`.
- يمثل التوثيق وظيفيا وشكليا، وليس كتطبيق إنتاجي نهائي.

## قواعد أساسية قبل أي تعديل

- قراءة التوثيق قبل تعديل أي شاشة:
  - `docs/en/technical/specification`
  - `docs/en/accounting`
  - النسخ العربية والفرنسية عند الحاجة للمطابقة اللغوية.
- الحفاظ على فصل الكود الحالي:
  - `prototype/core` للمنطق المشترك.
  - `prototype/views` لكل واجهة مستقلة.
  - `prototype/styles.css` للتصميم.
  - `prototype/bootstrap.js` لبدء التطبيق.
- أي إضافة وظيفية يجب أن تظهر في:
  - الواجهة المناسبة.
  - التقارير عند الحاجة.
  - الـ audit أو export history عند الحاجة.
  - لوحة Documentation Coverage إذا كانت تؤثر على التغطية.

## تغطية التوثيق المطلوبة

يجب أن يظل النموذج ممثلا لهذه المجالات:

- Product overview: الوحدات، المستخدمون، الفترات، حالة الشهر.
- Navigation and layout: top bar، side menu، action buttons، read-only state.
- Dashboard: cards، alerts، آخر تحديث، ربط البطاقات بمصدرها.
- Accounting interfaces: Cash Closing، Cash & Safe، Monthly Balance، Suppliers، Partners.
- Attendance and Salaries: grid، codes، totals، salary draft/validation/payment.
- Reports: كل التقارير المذكورة في التوثيق، مع preview، print، export، official trace.
- HR: employees، contracts، leave، documents، history.
- Administration: users، permissions، audit، periods، closing checklist.
- Business rules: calculations and validation messages.
- Open questions: تبقى ظاهرة ولا يتم تحويلها إلى قواعد نهائية إلا بعد قرار واضح.

## تحسين تجربة المستخدم

عند التوسيع، الأولوية ليست إضافة عناصر كثيرة فقط، بل جعل الاستخدام أوضح:

- اجعل كل شاشة تبدأ بالمعلومة الأكثر أهمية.
- اجعل الحقول المالية واضحة ومقروءة، مع totals قريبة من الجدول.
- لا تخف رسائل الأخطاء داخل الجداول؛ استخدم toast أو alert واضح.
- حافظ على read-only state عند إغلاق الشهر.
- اجعل الأزرار قصيرة وواضحة، ويفضل أن تكون action bars ثابتة في موضع منطقي.
- لا تضع شرحا تعليميا طويلا داخل التطبيق؛ اجعل الواجهة نفسها مفهومة.
- حافظ على responsive layout في الشاشات الصغيرة.
- لا تجعل الألوان كلها من نفس العائلة؛ استخدم palette متوازنة كما هو موجود حاليا.

## نقاط توسعة مقترحة

### Dashboard

- إضافة drill-down أدق لكل بطاقة.
- إظهار trend بسيط شهري إذا كانت هناك أكثر من فترة.
- تمييز alert severity حسب التأثير على closing.

### Cash Closing

- إضافة فلتر user/date.
- إظهار net difference لكل user مباشرة أعلى الجدول.
- تحسين مسار justification للفروقات.

### Cash & Safe

- تحسين عرض Safe Summary.
- فصل Safe Exits وProfitability Movements بصريا بشكل أوضح.
- إضافة source trace لكل مبلغ يدخل في Real Safe Net.

### Suppliers and Partners

- إضافة بحث وفلاتر حسب category/status.
- إظهار running remaining balance.
- إضافة attachment reference أكثر وضوحا للفواتير.

### Attendance and Salaries

- جعل attendance grid أكثر قابلية للإدخال السريع.
- إضافة totals حسب code لكل موظف.
- فصل salary additions/deductions بصريا.
- إضافة validate/pay actions بدل اختيار status فقط.

### Reports

- تحسين preview الرسمي.
- إضافة report status واضح: Draft أو Official.
- إضافة running balance في Cheque Statement عندما تتضح القاعدة.
- جعل CSV export أكثر شبها بـ Excel structure.

### HR

- تنظيم Employee File ك tabs فعلية:
  - Identity
  - Contract
  - Leave
  - Attendance
  - Salaries
  - Documents
  - History
- إضافة تنبيهات انتهاء العقود.

### Administration

- تحسين closing checklist ليعرض blockers أولا.
- إضافة audit details modal.
- إضافة إعدادات prototype مثل NIF/RIP واسم المستخدم الحالي.

## قرارات لا يجب افتراضها

لا يتم تثبيت هذه القرارات بدون طلب واضح من المستخدم:

- صيغة LAM Revenue النهائية.
- طريقة التعامل مع TPE.
- قواعد الرواتب الرسمية.
- أسعار الحراسة.
- قاعدة يوم 15 في الإجازات.
- طريقة SOFTLAM: manual أو import.
- صلاحية إغلاق أو إعادة فتح الشهر.

## معيار النجاح

يعتبر التوسيع ناجحا إذا تحقق الآتي:

- كل شاشة تعمل بدون أخطاء JavaScript.
- كل واجهة في `prototype/views` ترندر بشكل صحيح.
- كل تقرير في Reports يفتح preview.
- البيانات تحفظ وتقرأ من `localStorage`.
- الإغلاق الشهري يحترم checklist.
- المستودع ينتهي بحالة git نظيفة.
- يتم إنشاء commit بعد التعديل.

## فحوصات إلزامية قبل أي commit

```powershell
node --check prototype\app.js
node --check prototype\bootstrap.js
Get-ChildItem prototype\core\*.js | ForEach-Object { node --check $_.FullName }
Get-ChildItem prototype\views\*.js | ForEach-Object { node --check $_.FullName }
git diff --check
git status --short
```

ويجب أيضا تشغيل اختبار تحميل كل الواجهات والتقارير عند تعديل `core`, `views`, أو ترتيب scripts في `index.html`.
