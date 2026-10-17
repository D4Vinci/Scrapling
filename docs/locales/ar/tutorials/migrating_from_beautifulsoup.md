---
title: "الانتقال من BeautifulSoup إلى Scrapling"
description: "قارن مهام اختيار العناصر والنصوص والخصائص والتنقل الشائعة في BeautifulSoup بما يقابلها في Scrapling، مع أمثلة عملية لفروق API."
---

# الانتقال من BeautifulSoup إلى Scrapling {#migrating-from-beautifulsoup-to-scrapling}

إذا كنت تعرف BeautifulSoup بالفعل، فستجد ما يعجبك هنا. تعمل Scrapling بسرعة أكبر بكثير، وتوفر قدرات التحليل نفسها الموجودة في BS، مع قدرات إضافية لا توجد فيه، وميزات قوية لجلب صفحات الويب الحديثة والتعامل معها. يساعدك هذا الدليل على تعديل كود BeautifulSoup الحالي بسرعة للاستفادة من قدرات Scrapling.

يغطي الجدول التالي أشهر العمليات التي تستخدمها أثناء استخراج بيانات الصفحات. يوضح كل صف طريقة تنفيذ مهمة في BeautifulSoup والطريقة المقابلة في Scrapling.

ستلاحظ غياب بعض اختصارات BeautifulSoup من Scrapling. وهذا أحد أسباب أن BeautifulSoup أبطأ. الفكرة ببساطة: إذا أمكن تنفيذ الميزة نفسها في سطر قصير، فلا حاجة إلى التضحية بالأداء لتقصير هذا السطر أكثر :)

| المهمة | كود BeautifulSoup | كود Scrapling |
|-----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| استيراد المحلل | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| تحليل HTML من نص | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| العثور على عنصر واحد | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| العثور على عدة عناصر | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| العثور على عنصر واحد، مثال 2 | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| العثور على عنصر واحد، مثال 3 | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(lambda e: re.search(r"^b", e.tag) is not None)` |
| العثور على عنصر واحد، مثال 4 | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| العثور على عنصر واحد، مثال 5 | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| العثور على عنصر حسب نصه | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| استخدام CSS للعثور على أول عنصر مطابق | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| استخدام CSS للعثور على كل العناصر المطابقة | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| عرض مصدر الصفحة أو العنصر بتنسيق واضح | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| عرض مصدر الصفحة أو العنصر دون تحسين التنسيق | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
| قراءة اسم وسم العنصر | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| استخراج نص العنصر | `string = element.string`                                                                                     | `string = element.text`                                                           |
| استخراج كل النص في المستند أو داخل وسم | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| الوصول إلى قاموس الخصائص | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| استخراج الخصائص | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| الانتقال إلى العنصر الأب | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| قراءة كل أسلاف العنصر | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| البحث عن عنصر بين أسلاف العنصر | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| قراءة كل العناصر المجاورة | غير متاح                                                                                                           | `siblings = element.siblings`                                                     |
| قراءة العنصر المجاور التالي | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| البحث عن عنصر بين العناصر المجاورة | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| البحث عن عدة عناصر بين العناصر المجاورة | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| البحث عن عنصر بين العناصر التالية | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| البحث عن عدة عناصر بين العناصر التالية | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| البحث عن عنصر بين الأسلاف | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| البحث عن عدة عناصر بين الأسلاف | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| قراءة العنصر المجاور السابق | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| الانتقال إلى العناصر الأبناء | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| قراءة جميع العناصر التابعة | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| اختيار الروابط داخل فقرات story | `group = soup.select('p.story a')`                                                             | `group = page.css('p.story a')`              |

عند تمرير تعبير regex مُجمّع مباشرة إلى `find()` أو `find_all()` في Scrapling، فإنه يطابق نص العنصر، وليس اسم الوسم. استخدم دالة lambda الموضحة أعلاه لأسماء الوسوم، أو `page.find_by_regex(r"^b")` للبحث المباشر في النص.

¹ **ملاحظة:** تبحث `find_previous` و`find_all_previous` في BS4 في كل العناصر السابقة حسب ترتيب المستند. أما `path` في Scrapling فتُرجع الأسلاف فقط، أي سلسلة العناصر الآباء. لذا فهما ليستا متكافئتين تمامًا، لكن البحث في الأسلاف يغطي الحالة الأكثر شيوعًا.

**نقطة مهمة يجب تذكّرها**: توفر BeautifulSoup ميزات لتعديل الصفحة بعد تحليلها. أما Scrapling فتركز على استخراج البيانات بسرعة أكبر، ثم يمكنك فعل ما تريد بالبيانات الناتجة. كلتاهما تصلح لاستخراج بيانات الويب، لكن إحداهما متخصصة في هذا العمل :)

### تطبيق ذلك في مثال كامل {#putting-it-all-together}

إليك مثالًا بسيطًا لجلب صفحة واستخراج كل الروابط باستخدام BeautifulSoup وScrapling.

**باستخدام BeautifulSoup:**

```python
import requests
from bs4 import BeautifulSoup

url = 'https://example.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')
for link in links:
    print(link['href'])
```

**باستخدام Scrapling:**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)').getall()
for link in links:
    print(link)
```

كما ترى، تبسّط Scrapling العملية بجمع الجلب والتحليل في خطوة واحدة، فيصبح الكود أوضح وأكثر كفاءة.

!!! abstract "**ملاحظات إضافية:**"

    - **محللات مختلفة**: تسمح BeautifulSoup باختيار محرك التحليل، ومنها `lxml`. أما Scrapling فتستخدم مكتبة `lxml` افتراضيًا لأسباب تتعلق بالأداء.
    - **أنواع العناصر**: العناصر في BeautifulSoup هي كائنات `Tag`، وفي Scrapling هي كائنات `Selector`. لكنها توفر دوال وخصائص متشابهة للتنقل واستخراج البيانات.
    - **معالجة الأخطاء**: تُرجع المكتبتان `None` عندما لا يوجد العنصر، مثل `soup.find()` أو `page.find()`. في Scrapling، تُرجع `page.css()` قائمة `Selectors` فارغة إذا لم يوجد تطابق. ويمكنك استخدام `page.css('.foo').first` للحصول على أول نتيجة أو `None` بأمان. لتجنب الأخطاء، تحقّق من `None` أو النتائج الفارغة قبل الوصول إلى الخصائص.
    - **استخراج النصوص**: توفر Scrapling دوال إضافية لمعالجة النصوص عبر `TextHandler`، مثل `clean()` لإزالة المسافات الزائدة أو المتتالية أو المحارف غير المرغوبة. راجع التوثيق للاطلاع على القائمة الكاملة.

يوفر التوثيق تفاصيل أكثر عن ميزات Scrapling، والقائمة الكاملة للمعاملات التي يمكن تمريرها إلى الدوال.

يساعدك هذا الدليل على الانتقال من BeautifulSoup إلى Scrapling بسهولة. نتمنى لك تجربة موفقة في استخراج البيانات!
