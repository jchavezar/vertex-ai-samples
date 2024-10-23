import 'dart:convert';
import 'package:marketplace_ai/search_results.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart' show rootBundle;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
        theme: ThemeData(
            primarySwatch: Colors.deepOrange,
          appBarTheme: const AppBarTheme(
              backgroundColor: Colors.white //Example appBar color
          ),
          scaffoldBackgroundColor: Colors.white,
        ),
      home: const MyHomePage(),
        debugShowCheckedModeBanner: false
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Map<String, dynamic> dataset = {}; //
  bool isHovering = false;
  String inputMessage = "";

  Color x = Colors.deepOrange;

  @override
  void initState() {
    super.initState();
    _loadDataset(); // Load the dataset when the widget is initialized
  }

  Future<void> _loadDataset() async {
    try {
      String jsonString = await rootBundle.loadString('rag_data.json');
      setState(() {
        dataset = jsonDecode(jsonString);
      });
    } catch (e) {
      print('Error loading JSON: $e');
      // Handle error, e.g., show an error message to the user
    }
  }
  @override
  Widget build(BuildContext context) {
    var screenSize = MediaQuery.of(context).size;
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
      ),
      body: Center(
        child: Column(
          children: [
            const SizedBox(height: 35),
            AnimatedContainer(
                duration: const Duration(microseconds: 1),
              // padding: const EdgeInsets.all(8.0),
              height: 60,
              width: screenSize.width /2,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.black, width: 2.0),
                borderRadius: BorderRadius.circular(32.0)
              ),
              child: MouseRegion(
                  onEnter: (_) => setState(() => isHovering = true),
                  onExit: (_) => setState(() => isHovering = false),
                child: Row(
                  // alignment: Alignment.centerRight,
                  // mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      flex: 9,
                      child: Container(
                        padding: const EdgeInsets.only(left:15.0),
                        width: (screenSize.width /2)*.80,
                        child: TextField(
                          decoration: const InputDecoration(
                            hintText: "Search for anything",
                            border: InputBorder.none,
                              contentPadding: EdgeInsets.only(left: 15.0, right: 60)
                          ),
                          onSubmitted: (value) async {
                            var request = http.MultipartRequest('POST', Uri.parse("https://markeplace-basic-254356041555.us-east1.run.app/vais"), );
                            request.fields['text_data'] = value;
                            var streamedResponse = await request.send();

                            if (streamedResponse.statusCode == 200) {
                              var response = await http.Response.fromStream(streamedResponse);
                              Map<String, dynamic> responseBody = jsonDecode(response.body);
                              print(responseBody.keys);
                              dataset = {
                                "public_cdn_link": responseBody["public_cdn_link"],
                                "title": responseBody["title"],
                                "generated_title": responseBody["generated_title"],
                                "generated_description": responseBody["generated_description"],
                                "description": responseBody["description"],
                                "price_usd": responseBody["price_usd"],
                                "q_cat_1": responseBody["q_cat_1"],
                                "a_cat_1": responseBody["a_cat_1"],
                                "q_cat_2": responseBody["q_cat_2"],
                                "a_cat_2": responseBody["a_cat_2"],
                                "questions_only_cat3": responseBody["questions_only_cat3"],
                              };
                            }
                            else {
                              dataset = dataset;
                            }
                            setState(() {
                              inputMessage = value;
                            });
                          },
                        ),
                      ),
                    ),
                    Expanded(
                      flex: 1,
                      child: LayoutBuilder(
                        builder: (context, constraints) {
                          print(constraints.maxWidth);
                          return Stack(
                            alignment: Alignment.centerRight, // Align the stack to the right
                            children: [
                              AnimatedContainer(
                                duration: const Duration(milliseconds: 200),
                                width: isHovering ? 50*0.8 : 50*0.8,  // Width animates
                                height: isHovering ? 56 : 50*0.8,
                                margin: isHovering ? const EdgeInsets.only(right: 0) : const EdgeInsets.only(right: 5),
                                padding: isHovering ? const EdgeInsets.only(right: 10) : const EdgeInsets.only(left: 0),
                                decoration: BoxDecoration(
                                  borderRadius: isHovering
                                      ? const BorderRadius.only(
                                    topRight: Radius.circular(32),
                                    bottomRight: Radius.circular(32),
                                  )
                                      : BorderRadius.circular(32), // Full circle when not hovering
                                  color: isHovering
                                  ? const Color.fromRGBO(255, 87, 34, 0.5)
                                      : const Color.fromRGBO(255, 87, 34, 1.0)
                                  ,
                                ),
                                child: const Center(
                                  child: Icon(
                                    Icons.search,
                                    color: Colors.white,
                                    size: 25.0,
                                  ),
                                ),
                              ),
                            ],
                          );
                        }
                      ),
                    ),
                  ],
                )
              )
            ),
            Text(inputMessage),
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(14.0),
                // height:screenHeight*.80,
                child: GridView.builder(
                  shrinkWrap: true,
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 5,
                      crossAxisSpacing: 20.0,
                      mainAxisSpacing: 20.0,
                      mainAxisExtent: 240,
                    ),
                    itemCount: dataset["public_cdn_link"] != null ? dataset["public_cdn_link"].length : 0,
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
                                dataset["public_cdn_link"].elementAt(index),
                              height:200,
                              width: double.infinity,
                              fit: BoxFit.cover,
                            ),
                            onTap: (){
                              Navigator.of(context).push(MaterialPageRoute(builder: (BuildContext context) {
                                return ListingId(
                                  dataset: {
                                    "public_cdn_link": dataset["public_cdn_link"].elementAt(index),
                                    "generated_title": dataset["generated_title"].elementAt(index),
                                    "generated_description": dataset["generated_description"].elementAt(index),
                                    "description": (index >= 0 && index < dataset["description"].length)
                                        ? dataset["description"].elementAt(index)
                                        : "Description not available",
                                    "title": dataset["title"].elementAt(index),
                                    "price_usd": dataset["price_usd"].elementAt(index),
                                    "q_cat_1": dataset["q_cat_1"].elementAt(index),
                                    "a_cat_1": dataset["a_cat_1"].elementAt(index),
                                    "q_cat_2": dataset["q_cat_2"].elementAt(index),
                                    "a_cat_2": dataset["a_cat_2"].elementAt(index),
                                    "questions_only_cat3": dataset["questions_only_cat3"].elementAt(index),
                                  }
                                );
                              }));
                            }
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 15, right: 15, top: 15),
                          height:35,
                          // width: double.infinity,
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Flexible(
                                // width: 150,
                                  child: Text(dataset["title"].elementAt(index),
                                      overflow: TextOverflow.ellipsis),
                              ),
                              SizedBox(
                                width: 40,
                                child: Text(
                      (dataset.containsKey('price_usd') ?
                                    "\$${dataset['price_usd'].elementAt(index)}": 'price').trim(),
                                    overflow: TextOverflow.ellipsis)
                              )
                            ],
                          )
                        )
                      ],
                    ),
                  );
                }),
              ),
            )
          ],
        ),
      )
    );
  }
}
