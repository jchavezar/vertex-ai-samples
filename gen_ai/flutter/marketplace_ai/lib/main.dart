import 'dart:convert';
import 'package:marketplace_ai/search_results.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'Flutter Demo',
      home: MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;
  String inputMessage = "";
  Map<String, dynamic> dataset = {
    'image_uri': [
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
      'https://gcpetsy.sonrobots.net/etsy-10k-vais/il_570xN.1828850751_i1w1.jpg',
    ],
    'title': [
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
      'Vintage Tramp Art Baby Booties',
    ]
  };


  void _incrementCounter() {
    setState(() {
      // This call to setState tells the Flutter framework that something has
      // changed in this State, which causes it to rerun the build method below
      // so that the display can reflect the updated values. If we changed
      // _counter without calling setState(), then the build method would not be
      // called again, and so nothing would appear to happen.
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    var screenSize = MediaQuery.of(context).size;
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          children: [
            const SizedBox(height: 35),
            Container(
              padding: const EdgeInsets.all(8.0),
              height: 60,
              width: screenSize.width /2,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade400, width: 1.0),
                borderRadius: BorderRadius.circular(32.0)
              ),
              child: TextField(
                decoration: const InputDecoration(
                  prefixIcon: Icon(
                      Icons.search,
                    color: Colors.deepOrange,
                  ),
                  border: InputBorder.none,
                ),
                onSubmitted: (value) async {
                  print(value);
                  var request = http.MultipartRequest('POST', Uri.parse("http://0.0.0.0:8000/vais"));
                  request.fields['text_data'] = value;
                  var streamedResponse = await request.send();

                  if (streamedResponse.statusCode == 200) {
                    var response = await http.Response.fromStream(streamedResponse);
                    Map<String, dynamic> responseBody = jsonDecode(response.body);
                    for (var items in responseBody.keys) {
                      print(items);
                    };
                    dataset = {
                      "image_uri": responseBody["public_cdn_link"],
                      "title": responseBody["title"],
                      "generated_title": responseBody["generated_title"],
                      "generated_description": responseBody["generated_description"],
                      "price_usd": responseBody["price_usd"],
                    };
                  }
                  else {
                    dataset = dataset;
                  }
                  setState(() {
                    inputMessage = value;
                  });
                },
              )
            ),
            Text(inputMessage),
            Container(
              padding: const EdgeInsets.all(14.0),
              height:600,
              child: GridView.builder(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 5,
                    crossAxisSpacing: 20.0,
                    mainAxisSpacing: 20.0,
                    mainAxisExtent: 240,
                  ),
                  itemCount: dataset["image_uri"].length,
                  itemBuilder: (BuildContext context, int index) {
                return Container(
                  // padding: EdgeInsets.all(10.0),
                  decoration: BoxDecoration(
                    // border: Border.all(color: Colors.grey),
                      borderRadius: BorderRadius.circular(14.0)
                  ),
                  child: Column(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(16.0),
                        child: InkWell(
                          child: Image.network(
                              dataset["image_uri"].elementAt(index),
                            height:200,
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                          onTap: (){
                            Navigator.of(context).push(MaterialPageRoute(builder: (BuildContext context) {
                              return ListingId(
                                dataset: {
                                  "image_uri": dataset["image_uri"].elementAt(index),
                                  "generated_title": dataset["generated_title"].elementAt(index),
                                  "generated_description": dataset["generated_description"].elementAt(index),
                                  "title": dataset["title"].elementAt(index),
                                  "price_usd": dataset["price_usd"].elementAt(index),
                                }
                              );
                            }));
                          }
                        ),
                      ),
                      Container(
                        padding: EdgeInsets.only(left: 15, right: 15, top: 15),
                        height:35,
                        width: double.infinity,
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            SizedBox(
                              width: 150,
                                child: Text(dataset["title"].elementAt(index),
                                    overflow: TextOverflow.ellipsis),
                            ),
                            SizedBox(
                              width: 40,
                              child: Text(
                                  dataset.containsKey('price_usd') ?
                                  dataset['price_usd'].elementAt(index).toString(): 'price',
                                  overflow: TextOverflow.ellipsis)
                            )
                          ],
                        )
                      )
                    ],
                  ),
                );
              }),
            )
          ],
        ),
      )
    );
  }
}
