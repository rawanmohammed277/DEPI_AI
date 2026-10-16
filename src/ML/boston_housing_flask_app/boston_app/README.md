# Boston Housing — Flask App

تطبيق Flask كامل بيحل التاسك بتاع مشروع "Predicting Boston Housing Prices"
(Model Evaluation & Validation). كل الأجزاء الناقصة (TODO) في النوتبوك الأصلي
اتعملت جوه `model.py`، والـ `visuals.py` اتصلح (كان فيه أخطاء: `pl` مش
متعرّف، `curves.validation_curve` مش موجودة، و `ShuffleSplit` بتاريخة قديمة).

## هيكل المشروع

```
boston_app/
├── app.py              # سيرفر Flask (الصفحات + الروتس)
├── model.py             # كل حسابات الموديل (التاسك بالكامل)
├── visuals.py            # رسم learning curve و complexity curve
├── housing.csv           # الداتا
├── requirements.txt
├── static/style.css
└── templates/
    ├── base.html
    ├── index.html        # الصفحة الرئيسية: إحصائيات + فورم التوقع + الرسومات
    └── result.html        # نتيجة التوقع
```

## التشغيل

```bash
cd boston_app
pip install -r requirements.txt
python app.py
```

بعدين افتح المتصفح على:

```
http://127.0.0.1:5000
```

## اللي التطبيق بيعمله

- **إحصائيات الداتا**: أقل/أعلى سعر، المتوسط، الوسيط، الانحراف المعياري
  (كانت TODO في النوتبوك).
- **`performance_metric`**: R² score (`sklearn.metrics.r2_score`).
- **تقسيم الداتا**: `train_test_split` بنسبة 80/20.
- **`fit_model`**: `GridSearchCV` بيدور على أحسن `max_depth` (من 1 لـ 10)
  باستخدام `ShuffleSplit` (10 تقسيمات) كـ cross-validation.
- **فورم تفاعلي**: تدخل RM / LSTAT / PTRATIO ويطلعلك السعر المتوقع، مع 10
  محاولات (trials) بتوضح مدى استقرار التوقع (زي `PredictTrials` في
  النوتبوك الأصلي).
- **3 عملاء تجريبيين**: نفس الأرقام المذكورة في السؤال 10 بالنوتبوك.
- **رسمين بيانيين**: Learning Curves و Complexity Curve، بيتولّدوا live
  كـ PNG من `/plot/learning.png` و `/plot/complexity.png`.

## ملحوظة

السيرفر شغال بـ `debug=True` للتجربة المحلية بس. لو هتنشره فعليًا، شغّله
بـ WSGI server زي gunicorn وشيل `debug=True`.
