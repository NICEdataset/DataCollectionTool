# DataCollectionTool
This is the data collection tools used  for collecting NICE dataset ("https://nicedataset.github.io/index.html").

0. download raw [comments](https://files.pushshift.io/reddit/comments/) and [submissions](https://files.pushshift.io/reddit/submissions/) bz2 files.
1. filter submissions that contains image url.
  * see `src/extract_img.py`.
  * function `extract_submissions` extracts these submissions from the downloaded bz2 files
2. get text conversations for the filtered submissions.
  * see file `src/extract_conv.py`
  * firstly, do `extract_comments`, which extract comments given submissions
  * then, do `get_leaf_conv` which combines texts in the same submissions as conversations
3. download images for the filtered submissions.
  * see file `src/download.py`
  * this needs Imgur API, see [this](https://apidocs.imgur.com/) or [this](https://rapidapi.com/imgur/api/imgur-9/)
