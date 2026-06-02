# Prototype Expansion Prompts

هذه prompts موجهة إلى Codex عند العمل لاحقا على توسيع ModernLam web prototype. استخدمها كأوامر تشغيل تفصيلية، وليس كتوثيق نظري فقط.

كل prompt يفترض أن النموذج الحالي يعمل من `index.html`، وأن البيانات تحفظ في `localStorage`، وأن البنية مفصولة بين:

- `prototype/core`
- `prototype/views`
- `prototype/styles.css`
- `prototype/bootstrap.js`
- `index.html`

## Prompt 01 - Audit Documentation Coverage

```text
راجع كل توثيق ModernLam الحالي، خصوصا:
- docs/en/technical/specification
- docs/en/accounting
- docs/ar عند الحاجة للمطابقة اللغوية

ثم قارن كل بند موثق مع prototype الحالي.

المطلوب:
1. أنشئ جدول تغطية داخلي في النموذج أو حدّث جدول Documentation Coverage الموجود.
2. صنّف كل بند إلى:
   - Covered
   - Partially Covered
   - Tracked
   - Missing
3. لا تعتبر Open Questions مغطاة كقواعد نهائية، بل Tracked فقط.
4. أي Missing يجب أن يتحول إلى مهمة تنفيذية واضحة.
5. لا تغيّر قواعد غير محسومة مثل LAM Revenue أو الرواتب إلا إذا طلب المستخدم ذلك صراحة.

بعد التعديل:
- شغّل فحوصات JavaScript.
- اختبر رندر كل الواجهات.
- اختبر رندر كل التقارير.
- اعمل commit واضح.
```

## Prompt 02 - Improve Dashboard UX

```text
وسّع Dashboard ليكون مركز مراقبة شهري فعلي.

اعتمد على التوثيق:
- Dashboard summary cards
- alerts
- period status
- last update
- card opens source detail

المطلوب:
1. اجعل كل بطاقة قابلة للنقر وتفتح الشاشة المصدر.
2. أضف severity واضح للتنبيهات:
   - blocking
   - warning
   - info
3. اعرض تنبيهات:
   - unjustified cash differences
   - suppliers with remaining balance
   - subcontractors/conventions not settled
   - draft salaries
   - employees without active contract
   - incomplete cheques
   - missing report/export before closing
4. اجعل آخر تحديث واضحا.
5. لا تضف شرحا طويلا داخل الشاشة؛ واجهة Dashboard يجب أن تكون قابلة للفهم بسرعة.

تحقق من:
- dashboard renders.
- clicking cards changes view.
- closed month still read-only.
```

## Prompt 03 - Improve Cash Closing

```text
حسّن واجهة Cash Closing لتطابق التوثيق بشكل أقوى.

المطلوب:
1. أضف فلاتر حسب date وuser.
2. اجعل Difference Statement أكثر وضوحا:
   - total by user
   - positive difference
   - negative difference
   - net
3. عند وجود فرق بدون remark، اعرضه كـ blocking alert.
4. حافظ على قاعدة:
   Difference = Real Amount - Virtual Amount
5. لا تسمح بحفظ فرق غير صفري بدون remark.
6. اربط النتائج بتنبيهات Dashboard وMonthly Closing Checklist.

تحقق من:
- إدخال cash expense.
- إدخال difference = 0.
- رفض difference != 0 بدون remark.
- قبول difference != 0 مع remark.
```

## Prompt 04 - Improve Cash & Safe

```text
حسّن Cash & Safe حتى يكون source trace واضحا لكل حساب.

المطلوب:
1. اعرض Safe Summary بطريقة أوضح:
   - Real Safe Net
   - LAM Revenue
   - Convention Revenue
   - Subcontractor Revenue
   - Additional Entry Revenue
   - Global Revenue
2. أضف source trace لكل رقم رئيسي:
   - ما هي الجداول التي ساهمت فيه؟
   - ما هي القيم الداخلة والخارجة؟
3. حافظ على:
   Real Safe Net =
     Cash CV
     + Cash C
     + Paid Additional Entries
     + Profitability Movement
     + Paid Subcontractors
     + Paid Convention
     - Safe Exits
4. اعرض Total / Min / Max / Average مع استثناء الجمعة.
5. افصل Safe Exits وProfitability Movements بصريا.

لا تحسم صيغة LAM Revenue إذا بقيت مفتوحة في التوثيق؛ اعرضها كصيغة prototype فقط.
```

## Prompt 05 - Improve Suppliers and Partners

```text
وسّع Suppliers وSubcontractors & Conventions لتصبح أكثر قابلية للاستخدام.

المطلوب في Suppliers:
1. بحث وفلاتر حسب:
   - supplier
   - category
   - status
2. إظهار:
   - order total
   - paid
   - remaining balance
   - payment mode
   - reference
   - observation
3. دعم partial payments مع payments table.
4. تحديث status تلقائيا:
   - Paid
   - Partial
   - Unpaid

المطلوب في Partners:
1. فلتر حسب type:
   - Subcontractor
   - Convention
2. إظهار remaining balance بوضوح.
3. منع payment أكبر من remaining balance.
4. ربط payments بالـ audit.

تحقق من أن التقارير المرتبطة تتحدث بعد كل إدخال.
```

## Prompt 06 - Improve Attendance and Salaries

```text
حسّن Attendance وSalaries لتكون أقرب إلى workflow اليومي.

Attendance:
1. اجعل grid أسهل للإدخال السريع.
2. اعرض totals حسب code لكل موظف:
   - P
   - ABS
   - G
   - GV-J
   - GV-N
   - C
   - C.M
   - REC
   - P+
3. امنع codes غير معروفة.
4. اعرض empty days بشكل واضح.

Salaries:
1. افصل additions وdeductions بصريا.
2. أضف أزرار:
   - Validate
   - Mark Paid
3. اجعل salary formula ظاهرة كـ prototype formula وليس كقرار نهائي.
4. اربط draft salaries بقائمة إغلاق الشهر.

لا تثبت أسعار الحراسة أو قاعدة الرواتب الرسمية بدون قرار من المستخدم.
```

## Prompt 07 - Improve Reports and Printing

```text
حسّن Reports لتغطي التوثيق بالكامل بشكل عملي.

التقارير المطلوبة:
- Cash Expenses
- Differences
- Cash Movement
- Safe Movement
- Monthly Balance
- Supplier Journal
- Supplier Statement
- Subcontractor Statement
- Attendance
- Salary Report
- Service Vehicle
- Cheque Statement
- Encashment Statement
- Employees
- Contracts
- Leave

المطلوب:
1. كل تقرير له preview.
2. كل تقرير يظهر:
   - title
   - period
   - print date
   - user
   - table
   - totals
3. Official export يضيف trace في Export History.
4. CSV export يجب أن يكون قابلا للفتح في Excel.
5. Encashment Statement يجب أن يظهر:
   - ModernLam name
   - NIF
   - RIP
   - month/year
   - total
   - stamp/signature
6. Cheque Statement يجب أن يجهز مكان running balance، لكن لا تثبت القاعدة إذا لم تحسم.

اختبر كل report option واحدا واحدا.
```

## Prompt 08 - Improve HR Employee File

```text
حوّل HR إلى Employee File منظم وأكثر وضوحا.

المطلوب:
1. اجعل HR يحتوي tabs فعلية:
   - Identity
   - Contract
   - Leave
   - Attendance
   - Salaries
   - Documents
   - History
2. اعرض employee list مع:
   - active contract
   - leave balance
   - status
   - age
3. أضف تنبيهات:
   - no active contract
   - contract ending soon
   - no leave balance for current year
4. حافظ على قاعدة:
   To cannot be before From
   One active contract per employee
5. لا تجعل HR يرى/يعدل بيانات مالية إلا ضمن ما هو موثق.
```

## Prompt 09 - Improve Administration and Closing

```text
حسّن Administration بحيث تكون مركز التحكم في prototype.

المطلوب:
1. Users:
   - username
   - full name
   - role
   - active/inactive
2. Permissions Matrix:
   - مطابق للتوثيق
3. Audit Log:
   - creation
   - modification
   - cancellation
   - salary validation
   - monthly closing
   - reopening closed month
   - permission change
4. Periods:
   - month
   - year
   - status
   - opened/closed metadata
5. Closing Checklist:
   - اعرض blockers أولا
   - امنع closing إذا توجد blockers
   - اجعل status يتحول إلى Under review عند الفشل
6. Prototype Settings:
   - lab name
   - NIF
   - RIP
   - current user display name

أي تعديل في settings يجب أن يحفظ في localStorage ويظهر في التقارير.
```

## Prompt 10 - Improve UX and Visual Design

```text
راجع تجربة المستخدم في كل prototype.

المطلوب:
1. افحص كل شاشة على desktop وmobile.
2. تأكد من عدم وجود:
   - نصوص متداخلة
   - أزرار طويلة لا تتسع
   - جداول غير قابلة للقراءة
   - ألوان متشابهة جدا
3. اجعل:
   - totals قريبة من الجداول
   - primary action واضحا
   - destructive action مميزا
   - readonly state مفهوما
4. لا تضف landing page.
5. لا تضف شرحا تسويقيا.
6. لا تستخدم UI cards داخل cards.
7. حافظ على تطبيق عملي يبدأ مباشرة من Dashboard.

اختبر:
- mobile width
- desktop width
- print preview styles
```

## Prompt 11 - Add Prototype Data Scenarios

```text
وسّع seed data بحيث تغطي سيناريوهات واقعية من التوثيق.

أضف بيانات تجريبية لـ:
1. شهر open.
2. شهر under review.
3. شهر closed.
4. cash difference مبرر.
5. cash difference غير مبرر.
6. supplier paid.
7. supplier partial.
8. supplier unpaid.
9. subcontractor paid.
10. convention partial.
11. employee without active contract.
12. draft salary.
13. validated salary.
14. paid salary.
15. vehicle expense.
16. cheque statement row.
17. encashment row.

احرص أن seed data لا تكسر checklist بالكامل؛ يجب أن توجد حالات تظهر التنبيهات بشكل مفيد.
```

## Prompt 12 - Final Verification Before Commit

```text
قبل أي commit بعد توسيع prototype:

1. افحص syntax:
   node --check prototype\app.js
   node --check prototype\bootstrap.js
   Get-ChildItem prototype\core\*.js | ForEach-Object { node --check $_.FullName }
   Get-ChildItem prototype\views\*.js | ForEach-Object { node --check $_.FullName }

2. اختبر رندر كل الواجهات:
   - dashboard
   - cashClosing
   - cashSafe
   - balance
   - suppliers
   - partners
   - attendance
   - salaries
   - reports
   - hr
   - admin

3. اختبر كل reports:
   - encashment
   - supplier
   - supplierJournal
   - partner
   - cashExpenses
   - differences
   - cashMovement
   - safeMovement
   - balance
   - attendance
   - salary
   - vehicle
   - cheque
   - employees
   - contracts
   - leave

4. افحص Git:
   git diff --check
   git status --short

5. اكتب commit message واضحا يصف:
   - ما توسع
   - ما تحسن في UX
   - ما تغير في التغطية
```

## Prompt 13 - Guardrails for Unresolved Decisions

```text
راجع Open Questions قبل أي تعديل في الحسابات.

لا تحول هذه البنود إلى قواعد نهائية بدون موافقة المستخدم:
- LAM Revenue formula
- Cash CV/Cash C role
- TPE treatment
- Additional Entries treatment
- SOFTLAM import/manual source
- salary formula
- guard prices
- absence unit
- leave day 15 rule
- leave carry-over
- cheque running balance
- role authorized to close/reopen

إذا احتجت إلى تمثيلها في prototype:
1. اجعلها clearly marked as prototype assumption.
2. أضفها في Administration > Open Decisions.
3. لا تغير Documentation Coverage من Tracked إلى Covered إلا بعد حسم القرار.
```

## Prompt 14 - Commit Message Template

```text
استخدم هذا القالب عند عمل commit لتوسعة prototype:

Title:
Expand prototype <area> coverage and UX

Body:
- Extended documentation coverage for <docs section>.
- Improved <screen/report/workflow> UX by <specific improvement>.
- Preserved browser-only localStorage behavior.
- Kept unresolved decisions tracked without hard-coding final business rules.
- Verified JS syntax, all views, all reports, and git diff checks.
```
