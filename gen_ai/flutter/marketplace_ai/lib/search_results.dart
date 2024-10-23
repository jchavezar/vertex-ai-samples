import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';

class ListingId extends StatefulWidget {
  final Map<String, dynamic> dataset;
  const ListingId({super.key, required this.dataset});
  @override
  State<ListingId> createState() => _ListingIdState();
}

class _ListingIdState extends State<ListingId> {
  String response = "";
  bool _isExpanded = false;
  List<dynamic> images = [];
  final TextEditingController _textController = TextEditingController();

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  void _clearTextField() {
    setState(() {
      _textController.clear();
    });
  }

  void _insertText(String textToInsert) {
    Future.delayed(Duration.zero, () {  // Ensure TextField is initialized
      final currentText = _textController.text;
      final textSelection = _textController.selection;

      final start = textSelection.isValid ? textSelection.start : currentText.length;
      final end = textSelection.isValid ? textSelection.end : currentText.length;

      final newText = currentText.replaceRange(start, end, textToInsert);
      final newCursorPosition = start + textToInsert.length;

      setState(() {
        _textController.text = newText;
        _textController.selection = TextSelection.fromPosition(
          TextPosition(offset: newCursorPosition),
        );
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: LayoutBuilder(
        builder: (BuildContext context, BoxConstraints constraints) {
          if (constraints.maxWidth < 600) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(14.0),
              child: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                    child: Image.network(
                      widget.dataset["public_cdn_link"] ??
                          "https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg",
                    ),
                  ),
                  _buildContent(context, constraints),
                ],
              ),
            );
          } else {
            return Row(
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                    child: Image.network(
                      widget.dataset["public_cdn_link"] ??
                          "https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg",
                    ),
                  ),
                ),
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(14.0),
                    child: _buildContent(context, constraints),
                  ),
                ),
              ],
            );
          }
        },
      ),
    );
  }

  Widget _buildContent(BuildContext context, BoxConstraints constraints) {
    double screenWidth = MediaQuery.of(context).size.width;
    const double spaceBetween = 25.0;

    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 30),
        Text(
          "Low in stock, only 7 left",
          style: TextStyle(
            color: Colors.deepOrange.shade400,
            fontWeight: FontWeight.bold,
            fontSize: 26.0,
          ),
        ),
        const SizedBox(height: spaceBetween),
        Text(
          ("\$${widget.dataset["price_usd"]}").trim(),
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 26.0,
          ),
        ),
        const SizedBox(height: spaceBetween),
        Text(
          (widget.dataset["generated_title"] ?? "test").trim(),
          style: const TextStyle(
            fontSize: 20.0,
          ),
        ),
        const SizedBox(height: spaceBetween),
        Text(
          (widget.dataset["title"] ?? "test").trim(),
          style: const TextStyle(
            fontSize: 16.0,
          ),
        ),
        const SizedBox(height: spaceBetween),
        RichText(
          text: TextSpan(
            children: [
              const TextSpan(
                text: 'Description: ',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16.0,
                ),
              ),
              TextSpan(
                text: (widget.dataset["generated_description"] ?? "test").trim(),
                style: const TextStyle(fontSize: 16.0),
              ),
            ],
          ),
        ),
        const SizedBox(height: spaceBetween),
        ExpansionPanelList(
          expansionCallback: (int index, bool _) {
            setState(() {
              _isExpanded = !_isExpanded;
            });
          },
          children: [
            ExpansionPanel(backgroundColor: Colors.white, headerBuilder: (BuildContext context, bool isExpanded) {
              return const ListTile(
                title: Text("Original Description"),
              );
            },
                body: ListTile(
                  // title: Text("Item 1 child"),
                  subtitle: Text(widget.dataset["description"]),
                ),
              isExpanded: _isExpanded,
            )
          ],
        ),
        const SizedBox(height: spaceBetween),
        SizedBox(
          width: screenWidth * 0.50, // Use constraints.maxWidth for mobile
          child: Container(
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey),
              borderRadius: BorderRadius.circular(8.0),
            ),
            child: Row(
              children: [
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: SizedBox(
                    height: 40,
                    width: 40,
                    child: Image.asset(
                      "artifacts_etsymate.png", // Replace with your asset path
                      fit: BoxFit.contain,
                    ),
                  ),
                ),
                 Expanded(
                  child: TextField(
                    controller: _textController,
                    decoration: const InputDecoration(
                      hintText: "Looking for specific info? Ask Chatsy!",
                      hintStyle: TextStyle(fontSize: 15.0),
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.symmetric(
                          vertical: 12.0, horizontal: 8.0),
                    ),
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Icon(Icons.send, color: Colors.deepOrange),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: spaceBetween),
        if (response.isNotEmpty)
          Container(
            width: screenWidth * 0.50, // Use constraints.maxWidth for mobile
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                  width: 1.0, color: Colors.deepOrange.shade400),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Chatsy: ",
                  style: TextStyle(
                      color: Colors.deepOrange.shade400,
                      fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 10.0),
                Text(response, style: const TextStyle(fontSize: 15.0)),
                const SizedBox(height:10.0),
                if (images.isNotEmpty)
                  Center(
                    child: Wrap(
                      alignment: WrapAlignment.center,
                      runAlignment: WrapAlignment.center,
                      spacing: 10.0,
                      runSpacing: 10.0,
                      children: [
                        for (var imageUrl in images)
                          Image.network(imageUrl, width: 100, height: 100),
                      ],
                    ),
                  ),
              ],
            ),
          ),



        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Wrap(
            spacing: 10.0,
            runSpacing: 10.0,
            children: [
              for (var i = 0; i < (widget.dataset["q_cat_1"] ?? []).length; i++)
                ElevatedButton(
                  onPressed: () {
                    print(widget.dataset["a_cat_1"][i]);
                    setState(() {
                      response = widget.dataset["a_cat_1"][i];
                      images = [];
                      _clearTextField();
                      _insertText(widget.dataset["q_cat_1"][i]);
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.lightBlue.shade100,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(25)),
                    padding: const EdgeInsets.all(15),
                  ),
                  child: Text(widget.dataset["q_cat_1"][i].trim()),
                ),

              for (var i = 0; i < (widget.dataset["q_cat_2"] ?? []).length; i++)
                ElevatedButton(
                  onPressed: () {
                    setState(() {
                      response = widget.dataset["a_cat_2"][i];
                      images = [];
                      _clearTextField();
                      _insertText( widget.dataset["q_cat_2"][i]);
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red.shade100,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(25)),
                    padding: const EdgeInsets.all(15),
                  ),
                  child: Text(widget.dataset["q_cat_2"][i].trim()),
                ),

              for (var i = 0;
              i < (widget.dataset["questions_only_cat3"] ?? []).length;
              i++)
                ElevatedButton(
                  onPressed: () async {
                    var request = http.MultipartRequest('POST', Uri.parse("https://markeplace-basic-254356041555.us-east1.run.app/vais"), );
                    request.fields['text_data'] = widget.dataset["questions_only_cat3"][i];
                    var streamedResponse = await request.send();

                    if (streamedResponse.statusCode == 200) {
                      var response = await http.Response.fromStream(streamedResponse);
                      Map<String, dynamic> responseBody = jsonDecode(response.body);
                      images = responseBody["public_cdn_link"];
                    }
                    setState(() {
                      if (images.contains(widget.dataset["public_cdn_link"])) {
                        images.remove(widget.dataset["public_cdn_link"]);
                      };
                      images = images.sublist(0, 5);
                      response = "Here are the relevant results:";
                      _clearTextField();
                      _insertText( widget.dataset["questions_only_cat3"][i]);
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.yellow.shade50,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(25)),
                    padding: const EdgeInsets.all(15),
                  ),
                  child: Text(
                      widget.dataset["questions_only_cat3"][i]),
                ),


            ],
          ),
        ),

      ],
    );
  }
}