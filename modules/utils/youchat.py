from seleniumbase import SB
import json
import urllib
import argparse
import time


def you_message(text: str, out_type: str = "json", timeout: int = 20):
    """Function to send a message and get results from YouChat.com

    Args:
        text (str): text to send
        out_type (str): type of result (json, string). Defaults to 'json'.
        timeout (int): timeout in seconds to wait for a result. Defaults to 20.

    Returns:
        str: response of the message
    """
    qoted_text = urllib.parse.quote_plus(text)
    result = {}
    data = ""
    with SB(uc=True, xvfb=True, page_load_strategy="none") as sb:
        dummy_url = "https://you.com/favicon/favicon.ico"
        sb.open(dummy_url)
        sb.save_screenshot("sel_d.png")
        try:
            sb.load_cookies(name="cookies.txt")
        except Exception as e:
            pass

        sb.open(
            f"https://you.com/api/streamingSearch?q={qoted_text}&domain=youchat"
        )  # sb.uc_open_with_reconnect

        timeout_delta = time.time() + timeout
        stream_available = False
        while time.time() <= timeout_delta:
            # Try to easy solve captcha challenge
            # print(sb.get_page_source()) # Debug
            try:
                # sb.save_screenshot('sel.png') # Debug
                sb.uc_gui_click_captcha()
            except Exception:
                result["error"] = (
                    "Selenium was detected! Try again later. Captcha not solved automaticly."
                )

            if time.time() > timeout_delta:
                sb.save_screenshot("sel.png")  # Debug
                result["error"] = (
                    "Timeout while getting data from Selenium! Try again later."
                )

            try:
                sb.assert_text("event: youChatIntent", timeout=3)
                if "error" in result:
                    result.pop("error")
                data = sb.get_text("body pre")
                break
            except Exception:
                pass

        sb.save_cookies(name="cookies.txt")

        res_message = ""
        for line in data.split("\n"):
            if line.startswith("data: {"):
                json_data = json.loads(line[5:])
                if "youChatToken" in json_data:
                    res_message += json_data["youChatToken"]
        result["generated_text"] = res_message

        if out_type == "json":
            return json.dumps(result)
        else:
            str_res = (
                result["error"] if ("error" in result) else result["generated_text"]
            )
            return str_res


def read_cookies(p="cookies.txt"):
    cookies = []
    with open(p, "r") as f:
        for e in f:
            e = e.strip()
            if e.startswith("#"):
                continue
            k = e.split("\t")
            if len(k) < 3:
                continue  # not enough data
            # with expiry
            cookies.append(
                {"domain": k[0], "name": k[-2], "value": k[-1], "expiry": int(k[-3])}
            )
    return cookies


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("MESSAGE", help="Message to YouChat")
    parser.add_argument("-out_type", "-ot", help="Output type", default="json")
    parser.add_argument(
        "-timeout", "-t", help="Timeout to wait response", default=20, type=int
    )
    args = parser.parse_args()
    text = args.MESSAGE
    print(you_message(text, args.out_type, args.timeout))


if __name__ == "__main__":
    main_cli()
