from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup as bs
import requests
import os

app = Flask(__name__)


@app.route('/', methods=['GET'])
@cross_origin()
def home():
    return render_template("index.html")


@app.route("/review", methods=["POST", "GET"])
@cross_origin()
def review():

    if request.method == "POST":
        # ****************Function declaration start *******************************************************************
        # noinspection PyUnboundLocalVariable
        def scrapper(review_div, product_info_list):
            """
            review_div = comment_boxes
            name_div = name_boxes
            url = product_url
            product_info_list = list of product name,price,url in same sequence
            """

            try:
                cust_comment_head = "Not Available"
                cust_name = review_div.find("div", {"class": "row _2pclJg"}).p.text
                cust_rating = review_div.find("div", {"class": "hGSR34 E_uFuv _3-6Xp-"}).text
                cust_comment = review_div.find("div", {"class": "_2t8wE0"}).text.replace("READ MORE", "")
            except:
                try:
                    cust_comment_head = review_div.div.div.div.p.text
                    cust_name = review_div.find("div", {"class": "row _2pclJg"}).p.text
                    cust_rating = review_div.div.div.div.div.text
                    cust_comment = review_div.find("div", {"class": "qwjRop"}).text.replace("READ MORE", "")
                except:
                    pass

            final_dict = {"Product Name": product_info_list[0], "Product Price": product_info_list[1],
                          "Customer Name": cust_name,
                          "Rating": cust_rating, "Comment_head": cust_comment_head, "Comment": cust_comment,
                          "Product url": product_info_list[2]}

            return final_dict

        # *******************function declaration end ******************************************************************

        try:
            search_string = str(request.form["search_string"])
            search_url = "https://www.flipkart.com/search?q=" + search_string.replace(" ", "")
            try:
                search_full_html = requests.get(search_url)
                search_full_bs = bs(search_full_html.text, "html.parser")
                search_product_boxes = search_full_bs.find_all("div", {"class", "bhgxx2 col-12-12"})
            except:
                print("Exception occured ln 66: Check your internet connection")

            try:
                product_url = "https://www.flipkart.com" + search_product_boxes[4].div.div.div.a["href"]
                product_full_html = requests.get(product_url)
                product_full_bs = bs(product_full_html.text, "html.parser")
                name_boxes = product_full_bs.find("div", {"class": "_29OxBi"})
                prod_name = name_boxes.h1.text.replace("\xa0", " ")
                prod_price = name_boxes.find("div", {"class": "_1uv9Cb"}).div.text
                ProdUrl = product_url
                product_info = [prod_name, prod_price, ProdUrl]
                comment_boxes = product_full_bs.find_all("div", {"class": "_3nrCtb"})
            except Exception as e:
                print("exception occured ln 89 " + str(e))

            final_list_dict = []
            for comment_box in comment_boxes:
                try:
                    results = scrapper(comment_box, product_info)
                    final_list_dict.append(results)
                except Exception as e:
                    # print(e)
                    break
            if len(final_list_dict) < 1:
                final_result = {"Product Name": product_info[0], "Product Price": product_info[1],
                          "Customer Name": "Not Available",
                          "Rating": "No Review", "Comment_head": "No Comments", "Comment": "No Reviews",
                          "Product url": product_info[2]}
            else:
                final_result = final_list_dict
            #print(final_result)
            return render_template("results.html", f_result=final_result)
        except Exception as e:
            print("Main Exception occured " + str(e))
            return render_template("error.html")

    else:
        return render_template(("index.html"))


port = int(os.getenv("PORT")) #only for pivotal
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port) #only for pivotal
