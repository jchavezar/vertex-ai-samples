import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class NextPage extends StatefulWidget {
  final image_uri_1;
  final image_uri_2;
  final image_uri_3;
  final image_uri_4;
  final image_uri_5;
  final image_uri_6;
  final image_uri_7;
  final image_uri_8;
  final image_uri_9;
  final image_uri_10;
  final title;
  final price_per_night;
  final guests;
  final amenities;
  final nearby_neighbourhood;
  final description;

  const NextPage({
    super.key,
    this.image_uri_1,
    this.image_uri_2,
    this.image_uri_3,
    this.image_uri_4,
    this.image_uri_5,
    this.image_uri_6,
    this.image_uri_7,
    this.image_uri_8,
    this.image_uri_9,
    this.image_uri_10,
    this.title,
    this.price_per_night,
    this.guests,
    this.amenities,
    this.nearby_neighbourhood,
    this.description,
  });
  @override
  State<NextPage> createState() => _NextPageState();
}

class _NextPageState extends State<NextPage> {

  @override
  Widget build(BuildContext context) {
    double windowSize = MediaQuery.of(context).size.width;
    return Scaffold(
      body: ListView(
        scrollDirection: Axis.vertical,
        children: [
          Container(
              padding: const EdgeInsets.only(left: 70.0, right: 5.0, top: 15.0),
              height: windowSize*0.035,
              child: const Text(
                "Photos Listing",
                style: TextStyle(fontSize: 24.0, fontWeight: FontWeight.bold),
              )
          ),
          Row(
            children: [
              Container(
                  padding: const EdgeInsets.all(12.0),
                  margin: const EdgeInsets.only(left: 25.0, right: 25.0, top: 15.0),
                  height: windowSize*0.32,
                  width: windowSize*0.8*0.80,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Flexible(
                          flex: 50,
                          child: Container(
                            decoration: const BoxDecoration(
                                borderRadius: BorderRadius.only(topLeft: Radius.circular(12.0), bottomLeft: Radius.circular(12.0))
                            ),
                            child: Expanded(
                              child: ClipRRect(
                                borderRadius: const BorderRadius.only(
                                  topLeft: Radius.circular(11.0),
                                  bottomLeft: Radius.circular(11.0),
                                ),
                                child: Image.network(widget.image_uri_1,
                                    fit: BoxFit.fill
                                ),
                              ),
                            ),
                          )
                      ),
                      const SizedBox(width: 10),
                      Flexible(
                          flex: 25,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Image.network(widget.image_uri_2,
                                    fit: BoxFit.fill
                                ),
                              ),
                              const SizedBox(height: 10),
                              Expanded(
                                child: Image.network(widget.image_uri_3,
                                    fit: BoxFit.fill
                                ),
                              ),
                            ],
                          )
                      ),
                      const SizedBox(width: 10),
                      Flexible(
                          flex: 25,
                          child: Container(
                            decoration: const BoxDecoration(
                                borderRadius: BorderRadius.only(topRight: Radius.circular(12.0), bottomRight: Radius.circular(12.0))
                            ),
                            //height: windowSize*0.3,
                            //width: windowSize*0.8,
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: ClipRRect(
                                    borderRadius: const BorderRadius.only(topRight: Radius.circular(11.0)),
                                    child: Image.network(widget.image_uri_4,
                                        fit: BoxFit.fill
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 10),
                                Expanded(
                                  child: ClipRRect(
                                    borderRadius: const BorderRadius.only(bottomRight: Radius.circular(11.0)),
                                    child: Image.network(widget.image_uri_5,
                                        fit: BoxFit.fill
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          )
                      ),
                    ],
                  )
              ),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(12.0),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.grey.withOpacity(0.5), // Shadow color
                        spreadRadius: 2, // How much the shadow spreads
                        blurRadius: 5, // How blurry the shadow is
                        offset: const Offset(0, 3), // Shadow offset (vertical in this case)
                      ),
                    ],
                  ),
                  margin: const EdgeInsets.only(top: 15.0, right: 20.0),
                  padding: const EdgeInsets.all(12.0),
                  height: windowSize*0.32,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text("Description", style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.bold),),
                      Text("${widget.description}"),
                      const SizedBox(height:12),
                      const Text("Title", style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.bold),),
                      Text("${widget.title}"),
                      const SizedBox(height:12),
                      const Text("Price", style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.bold),),
                      Text("${widget.price_per_night}"),
                      const SizedBox(height:12),
                      const Text("Maximum Guests Number", style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.bold),),
                      Text("${widget.guests}"),
                      const SizedBox(height:12),
                      const Text("Amenities", style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.bold),),
                      Wrap(
                        spacing: 8.0,
                        children: widget.amenities.replaceAll(RegExp(r"[\[\]']"), '').trim().split('  ').map<Widget>((amenity) => // Specify the type
                        Text(amenity.trim(), style: const TextStyle(fontSize: 14.0))
                        ).toList(), // Convert to List<Widget>
                      ),
                      const SizedBox(height:12),
                      const Text("Neighbourhood", style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.bold),),
                      Wrap(
                        spacing: 8.0,
                        children: widget.nearby_neighbourhood.replaceAll(RegExp(r"[\[\]']"), '').trim().split('  ').map<Widget>((nearby_neighbourhood) => // Specify the type
                        Text(nearby_neighbourhood.trim(), style: const TextStyle(fontSize: 14.0))
                        ).toList(), // Convert to List<Widget>
                      ),
                    ],
                  ),
                ),
              )
            ],
          ),
          Row(
            children: [
              Container(
                  padding: const EdgeInsets.all(12.0),
                  margin: const EdgeInsets.only(left: 25.0, right: 25.0, top: 15.0),
                  height: windowSize*0.32,
                  width: windowSize*0.8*0.8,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Flexible(
                          flex: 50,
                          child: Container(
                            decoration: const BoxDecoration(
                                borderRadius: BorderRadius.only(topLeft: Radius.circular(12.0), bottomLeft: Radius.circular(12.0))
                            ),
                            child: Expanded(
                              child: ClipRRect(
                                borderRadius: const BorderRadius.only(
                                  topLeft: Radius.circular(11.0),
                                  bottomLeft: Radius.circular(11.0),
                                ),
                                child: Image.network(widget.image_uri_6,
                                    fit: BoxFit.fill
                                ),
                              ),
                            ),
                          )
                      ),
                      const SizedBox(width: 10),
                      Flexible(
                          flex: 25,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Image.network(widget.image_uri_7,
                                    fit: BoxFit.fill
                                ),
                              ),
                              const SizedBox(height: 10),
                              Expanded(
                                child: Image.network(widget.image_uri_8,
                                    fit: BoxFit.fill
                                ),
                              ),
                            ],
                          )
                      ),
                      const SizedBox(width: 10),
                      Flexible(
                          flex: 25,
                          child: Container(
                            decoration: const BoxDecoration(
                                borderRadius: BorderRadius.only(topRight: Radius.circular(12.0), bottomRight: Radius.circular(12.0))
                            ),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: ClipRRect(
                                    borderRadius: const BorderRadius.only(topRight: Radius.circular(11.0)),
                                    child: Image.network(widget.image_uri_9,
                                        fit: BoxFit.fill
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 10),
                                Expanded(
                                  child: ClipRRect(
                                    borderRadius: const BorderRadius.only(bottomRight: Radius.circular(11.0)),
                                    child: Image.network(widget.image_uri_10,
                                        fit: BoxFit.fill
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          )
                      ),
                    ],
                  )
              ),
              const SizedBox(width: 200,)
            ],
          ),
          const SizedBox(height: 10.0),
        ],
      ),
    );
  }
}
