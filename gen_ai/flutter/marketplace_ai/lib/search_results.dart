import 'package:flutter/material.dart';

class ListingId extends StatefulWidget {
  final Map<String, dynamic> dataset;
  const ListingId({super.key, required this.dataset});
  @override
  State<ListingId> createState() => _ListingIdState();
}

class _ListingIdState extends State<ListingId> {
  @override
  Widget build(BuildContext context) {
    double screenWidth = MediaQuery.of(context).size.width;
    double screenHeight = MediaQuery.of(context).size.height;
    const double spaceBetween = 25.0;
    print(widget.dataset);
    return Scaffold(
      body: Row(
        children: [
          Center(
            child: Container(
              height: screenHeight*.80,
              width: screenWidth*.48,
              child: Image.network(
                  widget.dataset["image_uri"] ?? "https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg"
              ),
            )
          ),
          Container(
            height: screenHeight*.80,
            width: screenWidth*.50,
            padding: const EdgeInsets.all(14.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                    "Low in stock, only 7 left",
                    style: TextStyle(
                      color: Colors.deepOrange.shade400,
                      fontWeight: FontWeight.bold,
                      fontSize: 26.0,
                    )
                ),
                const SizedBox(height: spaceBetween),
                Text(
                  (widget.dataset["generated_title"] ?? "test").trim(),
                    style: const TextStyle(
                      fontSize: 20.0,
                    )
                ),
                const SizedBox(height: spaceBetween),
                Text(
                    (widget.dataset["title"] ?? "test").trim(),
                    style: const TextStyle(
                      fontSize: 18.0,
                    )
                ),
                const SizedBox(height: spaceBetween),
                RichText(
                  text: TextSpan(
                    children: [
                      const TextSpan(
                        text: 'Description: ',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18.0,
                        ),
                      ),
                      TextSpan(
                        text: (widget.dataset["generated_description"] ?? "test").trim(),
                        style: const TextStyle(
                          fontSize: 18.0,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: spaceBetween),
                Container(
                  width:screenWidth*.50,
                  child: Row(
                    children: [
                      SizedBox(
                          height: 50,
                          width: 50,
                          child:Image.network(
                              "https://gcpetsy.sonrobots.net/artifacts/etsymate.png",
                              fit:BoxFit.contain,
                            cacheWidth: 100,
                            cacheHeight: 100,
                          )
                      ),
                      const Expanded(
                        child: TextField(
                          decoration: InputDecoration(
                            hintText: "Looking for specific info? Ask Chatsy!",
                            hintStyle: TextStyle(fontSize: 14.0),
                          ),
                          // minLines: 1,
                          // maxLines:10,
                        ),
                      ),
                    ],
                  ),
                )
              ],
            )
          ),
        ],
      ),
    );
  }
}
