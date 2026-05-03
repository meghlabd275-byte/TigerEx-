package com.tigerex.admin.di

import android.content.Context
import com.tigerex.admin.api.TigerExAdminApi
import com.tigerex.admin.services.PreferencesService
import com.tigerex.admin.utils.Constants
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(
        loggingInterceptor: HttpLoggingInterceptor,
        preferencesService: PreferencesService,
        @ApplicationContext context: Context
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .addInterceptor { chain ->
                val token = kotlinx.coroutines.runBlocking {
                    preferencesService.getAccessTokenSync()
                }
                val request = chain.request().newBuilder().apply {
                    token?.let {
                        addHeader("Authorization", "Bearer $it")
                    }
                    addHeader("Content-Type", "application/json")
                    addHeader("Accept", "application/json")
                    addHeader("X-App-Version", "1.0.0")
                    addHeader("X-Platform", "android")
                }.build()
                chain.proceed(request)
            }
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(Constants.API_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideTigerExAdminApi(retrofit: Retrofit): TigerExAdminApi {
        return retrofit.create(TigerExAdminApi::class.java)
    }

    @Provides
    @Singleton
    fun providePreferencesService(@ApplicationContext context: Context): PreferencesService {
        return PreferencesService(context)
    }
}fun createWallet(): Wallet {
    val chars = "0123456789abcdef"
    val address = "0x" + (0 until 40).map { chars.random() }.joinToString("")
    val seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet(address, seed.split(" ").take(24).joinToString(" "), "USER_OWNS")
}
