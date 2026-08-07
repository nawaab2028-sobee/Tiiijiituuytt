FROM harshpreets63/random:simple

WORKDIR /usr/src/app

COPY . .

RUN pip3 install -r requirements.txt

# Sync container clock with real time before starting the bot.
# Fixes: pyrogram.errors.BadMsgNotification: [16] The msg_id is too low,
# the client time has to be synchronized. This happens when the container's
# system clock drifts from real time, which Telegram's servers reject.
RUN apt-get update && apt-get install -y --no-install-recommends ntpdate && rm -rf /var/lib/apt/lists/*

CMD ntpdate -u pool.ntp.org || ntpdate -u time.google.com || true; python3 -m bot