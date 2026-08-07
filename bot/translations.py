class Messages:

    IMAGE_LIST = [
        "https://graph.org/file/28339f6c961ca96a84f47-1a070fdc1632724513.jpg",
        "https://graph.org/file/b07088988e66447aeb92f-f8c4f26ad5b867aa5a.jpg",
        "https://graph.org/file/1f2bd4b7d0747a432e3fe-b1229343f6557ba344.jpg",
        "https://graph.org/file/ce8ebdb5c2ba8932ec780-1737059c6bb976617d.jpg",
        "https://graph.org/file/41b150f2461004c4fd99a-d29d2bc307f0fe6491.jpg",
        "https://graph.org/file/7831481e4c899748ee8a1-b976b5e72df8c3618c.jpg",
        "https://graph.org/file/1d1dab8f4dc33df10e38c-a3c92d386be28422ac.jpg",
        "https://graph.org/file/a1c4b27984bb61183048c-d11e4d6c9ea09fcedb.jpg",
        "https://graph.org/file/1d1548631e6d1d3b3796e-b6647f0434c20f100a.jpg",
        "https://graph.org/file/9db3816e75336ecc45959-6d49ddd4d0e92f1aae.jpg",
    ]

    START_MSG = (
        "**__Hi there {}.\n\nI'm Advanced Youtube Uploader Bot. Made with ❤️ by @SmartBoy_ApnaMS. You can use me to upload any telegram video to youtube once you authorise me.__**"
        "\n\n**__You can know more from /help.__**"
        "\n**__Or use /login to get started.__**"
    )

    HELP_MSG = [
        ".",
        "Hi there.\n\nFirst things first. You should be aware that youtube processes each and every video uploaded, "
        "and its AI is amazing that it flags the video for copyrights if it finds copywrited content as soon as its "
        "uploaded, and you will not be able to publish the video.\n\nRead through all the pages to know how I work.",
        "**Lets learn how I work.**\n\n**Step 1:** __You authorise me to upload to your youtube channel. More about "
        "this in comming pages.__\n\n**Step 2:** __You forward any Telegram video to me.__\n\n**Step 3:** __You reply __"
        "__/upload __to the forwarded video file. You can also specify some title in the upload command, but its "
        "optional though. Title will follow the __`/upload`. __If no title is given, filename will be used as title.__"
        "\n\n**Step 4:** __I remotely download the file and uploads to your Youtube channel.__\n\n**Step 5:** __I "
        "send you the Youtube link after upload.__",
        "**Create your youtube channel**\n\nThere is no point in using me if you dont have a Youtube Channel. So go "
        "through the given steps to create one.\n\n**Step 1:** __Sign in to YouTube on a computer or using the mobile."
        "__\n\n**Step 2:** __Try any action that requires a channel, such as uploading a video, posting a comment, "
        "or creating a playlist.__\n\n**Step 3:** __If you don't yet have a channel, you'll see a prompt to create "
        "a channel.__\n\n**Step 4:** __Check the details and confirm to create your new channel.__",
        "**Verify your YouTube account**\n\nYoutube take spam and abuse very seriously. So you are asked to verify "
        "your Youtube account. Once you've verified your account, you will be able to upload videos longer than 15 "
        "minutes. If you haven't verified your account every video uploaded which are longer than 15 minutes will be "
        "removed.\n[Verify your Youtube account here.](http://www.youtube.com/verify)\n\n__Remember to verify your "
        "project, else your uploads will be kept private.__",
        "**Now lets authorise.**\n\nYou need to give me the access to upload videos to your Youtube account. For that "
        "open the given link and allow access and copy the code. Come back here and type `/authorise` `copied-code` and "
        "send it.\n\n**Fear not!**\nI'm not a hacker or someone who wants to creep into people's privacy. I respect "
        "one's privacy. I'm here just to help anyone who wants help. If I was a hacker I won't be sitting here "
        "writing Telegram Bots.",
    ]

    LOGIN_MSG = (
          "**__You Want To Login. Great.__**"
          "\n\n**__You need to give me the access to upload videos to your Youtube account.\n\nFor that open the given button below and allow access and copy the code. Come back here and send your code in this formate:\n /authorise your_code (eg: 4/4waa...)__**"
    )

    NOT_A_REPLY_MSG = "Please reply to some video file."

    NOT_A_MEDIA_MSG = "No media file found. " + NOT_A_REPLY_MSG

    NOT_A_VALID_MEDIA_MSG = "This is not a valid media"

    DAILY_QOUTA_REACHED = "Looks like you are trying to upload more than 15 videos today! By default youtube only allows about 15 uploads daily, so this request might fail!!"

    PROCESSING = "Processing.....🤭"

    NOT_AUTHENTICATED_MSG = "You have not authenticated me to upload video to any account. see /help to authenticate"

    NO_AUTH_CODE_MSG = "There is no code. Please provide some code"

    AUTH_SUCCESS_MSG = "Congrats, you have successfully authenticated me to upload to Youtube.\nHappy uploading!"

    AUTH_FAILED_MSG = "Authentication failed\nDetails:{}"

    AUTH_DATA_SAVE_SUCCESS = "Successfully saved the given auth data!"

    NON_AUTH_START_MSG = (
        "Sorry Dude 😎\n"
        "**You are a Normal Member 🥸**\n"
        "So that i can't Help You 🫣\n\n"
        "If you want to Becomes Member of this Bot to Buy a Membership from my owner\n\n"
        "**My Owner Id:**\n"
        "@SmartBoy_ApnaMS\n\n"
        "Message Him without any fear and get a Membership then Resend me /Start or "
        "/Help **i will Do my Best For you** 🥰."
    )
