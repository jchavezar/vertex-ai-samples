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
  Map<String, dynamic> recDataset = {}; //
  bool isHovering = false;
  String inputMessage = "";
  bool showHomeLivingSection = true;
  Color x = Colors.deepOrange;
  final TextEditingController _textEditingController = TextEditingController();


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

  Future<Map<String, dynamic>> _ragSearch(String value) async {
    final url = Uri.parse("https://etsy-middleware.sonrobots.net/vais"); // Correct URL - removed revision

    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded', // Or 'application/json' if your backend prefers JSON
        },
        body: {
          'text_data': value,
        },
      );

      if (response.statusCode == 200) {
        final responseBody = jsonDecode(response.body);
        dataset = { //removed redundancies and unneeded entries
          "public_cdn_link": responseBody["public_cdn_link"],
          "title": responseBody["title"],
          "generated_title": responseBody["generated_title"],
          "generated_description": responseBody["llm_generated_description"],
          "description": responseBody["description"],
          "price_usd": responseBody["price_usd"],
          "questions_cat1": responseBody["questions_cat1"],
          "answers_cat1": responseBody["answers_cat1"],
          "questions_cat2": responseBody["questions_cat2"],
          "answers_cat2": responseBody["answers_cat2"],
          "questions_only_cat3": responseBody["questions_only_cat3"],
          "generated_rec": responseBody["generated_rec"],
        };
        return dataset;
      } else {
        print('Request failed with status: ${response.statusCode}. Body: ${response.body}');
        throw Exception('Failed to load data: ${response.statusCode}');
      }
    } catch (e) {
      print('Error during RAG search: $e');
      rethrow; // Re-throw the exception to be handled higher up
    }
  }

  @override
  Widget build(BuildContext context) {
    var screenSize = MediaQuery.of(context).size;
    bool isSmallScreen = screenSize.width < 600;
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
      ),
      body: Center(
        child: Column(
          children: [
            const SizedBox(height: 35),
            AnimatedContainer(
              // padding: isSmallScreen ?
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
                            controller: _textEditingController,
                            decoration: const InputDecoration(
                            hintText: "Search for anything",
                            border: InputBorder.none,
                              contentPadding: EdgeInsets.only(left: 15.0, right: 60)
                          ),
                          onSubmitted: (value) async {
                            dataset = await _ragSearch(value);
                            setState(() {
                              inputMessage = value;
                              showHomeLivingSection = false;
                            });
                          },
                        ),
                      ),
                    ),
                    Expanded(
                      flex: 1,
                      child: LayoutBuilder(
                        builder: (context, constraints) {
                          return Stack(
                            alignment: Alignment.centerRight, // Align the stack to the right
                            children: [
                              GestureDetector(
                                child: MouseRegion(
                                  cursor: SystemMouseCursors.click,
                                  child: AnimatedContainer(
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
                                    child: Center(
                                      child: Icon(
                                        Icons.search,
                                        color: Colors.white,
                                        size: isSmallScreen ? 15.0 : 25.0,
                                      ),
                                    ),
                                  ),
                                ),
                                onTap: () async {
                                  dataset = await _ragSearch(_textEditingController.text);
                                  setState(() {
                                    inputMessage = _textEditingController.text;
                                    showHomeLivingSection = false;
                                  });
                                },
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
            const SizedBox(height:30),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    if (showHomeLivingSection)
                      const Center(
                      child: Text("Home & Living", style: TextStyle(fontSize: 26.0)),
                    ),
                    if (showHomeLivingSection)
                      const SizedBox(height: 10),
                    if (showHomeLivingSection)
                      const Text("Kitchen and dining, storage solutions, rugs, lighting, wall decor, and furniture—everything you need to make your home yours"),
                    // if (showHomeLivingSection)
                    //   const SizedBox(height: 45),
                    // if (showHomeLivingSection)
                    //   Wrap(
                    //   spacing: 20.0,
                    //   children: [
                    //     SizedBox(
                    //       height:230,
                    //         width:150,
                    //         child: Column(
                    //           children: [
                    //             Container(
                    //               decoration: BoxDecoration(borderRadius: BorderRadius.circular(16.0)),
                    //               height: 200,
                    //               width: 150,
                    //               child: ClipRRect(
                    //                   borderRadius: BorderRadius.circular(16.0),
                    //                 child: Image.asset(
                    //                     "home_decor.jpeg",
                    //                   fit: BoxFit.fill
                    //                 ),
                    //               ),
                    //             ),
                    //             const SizedBox(height:10),
                    //             const SizedBox(
                    //               height: 20,
                    //                 child: Center(child: Text("Home Decor", style: TextStyle(fontSize: 16),))
                    //             )
                    //           ],
                    //         )
                    //     ),
                    //     SizedBox(
                    //       height:230,
                    //         width:150,
                    //         child: Column(
                    //           children: [
                    //             Container(
                    //               decoration: BoxDecoration(borderRadius: BorderRadius.circular(16.0)),
                    //               height: 200,
                    //               width: 150,
                    //               child: ClipRRect(
                    //                   borderRadius: BorderRadius.circular(16.0),
                    //                 child: Image.asset(
                    //                     "lighting.jpeg",
                    //                   fit: BoxFit.fill
                    //                 ),
                    //               ),
                    //             ),
                    //             const SizedBox(height:10),
                    //             const SizedBox(
                    //               height: 20,
                    //                 child: Center(child: Text("Lighting", style: TextStyle(fontSize: 16),))
                    //             )
                    //           ],
                    //         )
                    //     ),
                    //     SizedBox(
                    //         height:230,
                    //         width:150,
                    //         child: Column(
                    //           children: [
                    //             Container(
                    //               decoration: BoxDecoration(borderRadius: BorderRadius.circular(16.0)),
                    //               height: 200,
                    //               width: 150,
                    //               child: ClipRRect(
                    //                 borderRadius: BorderRadius.circular(16.0),
                    //                 child: Image.asset(
                    //                     "outdoor.jpeg",
                    //                     fit: BoxFit.fill
                    //                 ),
                    //               ),
                    //             ),
                    //             const SizedBox(height:10),
                    //             const SizedBox(
                    //                 height: 20,
                    //                 child: Center(child: Text("Outdoor & Gardening", style: TextStyle(fontSize: 16),))
                    //             )
                    //           ],
                    //         )
                    //     ),
                    //     SizedBox(
                    //         height:230,
                    //         width:150,
                    //         child: Column(
                    //           children: [
                    //             Container(
                    //               decoration: BoxDecoration(borderRadius: BorderRadius.circular(16.0)),
                    //               height: 200,
                    //               width: 150,
                    //               child: ClipRRect(
                    //                 borderRadius: BorderRadius.circular(16.0),
                    //                 child: Image.asset(
                    //                     "furniture.jpeg",
                    //                     fit: BoxFit.fill
                    //                 ),
                    //               ),
                    //             ),
                    //             const SizedBox(height:10),
                    //             const SizedBox(
                    //                 height: 20,
                    //                 child: Center(child: Text("Furniture", style: TextStyle(fontSize: 16),))
                    //             )
                    //           ],
                    //         )
                    //     ),
                    //     SizedBox(
                    //         height:230,
                    //         width:150,
                    //         child: Column(
                    //           children: [
                    //             Container(
                    //               decoration: BoxDecoration(borderRadius: BorderRadius.circular(16.0)),
                    //               height: 200,
                    //               width: 150,
                    //               child: ClipRRect(
                    //                 borderRadius: BorderRadius.circular(16.0),
                    //                 child: Image.asset(
                    //                     "storage.jpeg",
                    //                     fit: BoxFit.fill
                    //                 ),
                    //               ),
                    //             ),
                    //             const SizedBox(height:10),
                    //             const SizedBox(
                    //                 height: 20,
                    //                 child: Center(child: Text("Storage & Organ", style: TextStyle(fontSize: 16),))
                    //             )
                    //           ],
                    //         )
                    //     ),
                    //   ],
                    // ),
                    const SizedBox(height: 35),
                    Padding(
                      padding: const EdgeInsets.only(left: 25.0, right: 25.0),
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
                                  onTap: () {
                                    Navigator.of(context).push(MaterialPageRoute(builder: (BuildContext context) {
                                      return ListingId(
                                        dataset: {
                                          "public_cdn_link": dataset["public_cdn_link"].elementAt(index),
                                          "generated_title": dataset["generated_title"].elementAt(index),
                                          "generated_description": dataset["generated_description"]?.elementAt(index) ?? "Description not available",
                                          "description": (index >= 0 && index < dataset["description"].length)
                                              ? dataset["description"].elementAt(index)
                                              : "Description not available",
                                          "title": dataset["title"].elementAt(index),
                                          "price_usd": dataset["price_usd"].elementAt(index),
                                          "q_cat_1": dataset["questions_cat1"].elementAt(index),
                                          "a_cat_1": dataset["answers_cat1"].elementAt(index),
                                          "q_cat_2": dataset["questions_cat2"].elementAt(index),
                                          "a_cat_2": dataset["answers_cat2"].elementAt(index),
                                          "questions_only_cat3": dataset["questions_only_cat3"].elementAt(index),
                                          // "rec_data": recDataset,
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
                  ],
                ),
              ),
            )
          ],
        ),
      )
    );
  }
}
